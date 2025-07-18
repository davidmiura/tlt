from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import discord
from tlt.adapters.discord_adapter.bot_manager import bot
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()

class ExperienceCreate(BaseModel):
    message_id: int
    user_id: int
    rating: int  # 1-5
    feedback: str
    photos: Optional[List[str]] = None

class ExperienceResponse(BaseModel):
    experience_id: str
    message_id: int
    user_id: int
    rating: int
    feedback: str
    photos: Optional[List[str]]
    created_at: datetime

@router.post("/", response_model=ExperienceResponse)
async def create_experience(experience: ExperienceCreate):
    """Create a new experience for an event"""
    if experience.message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        event = bot.active_events[experience.message_id]
        guild = bot.get_guild(event["guild_id"])
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        user = guild.get_member(experience.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Validate rating
        if not 1 <= experience.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
            
        # Create experience ID
        experience_id = f"{experience.message_id}_{experience.user_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Store experience
        experience_data = {
            "message_id": experience.message_id,
            "user_id": experience.user_id,
            "rating": experience.rating,
            "feedback": experience.feedback,
            "photos": experience.photos,
            "created_at": datetime.now(timezone.utc)
        }
        bot.experiences[experience_id] = experience_data
        
        # Create thread for the experience if it doesn't exist
        channel = guild.get_channel(event["channel_id"])
        if channel:
            message = await channel.fetch_message(experience.message_id)
            
            # Check if thread already exists
            thread_name = f"Experiences: {event['topic']}"
            existing_thread = discord.utils.get(message.threads, name=thread_name)
            
            if not existing_thread:
                # Create new thread
                thread = await message.create_thread(
                    name=thread_name,
                    auto_archive_duration=10080  # 7 days
                )
            else:
                thread = existing_thread
                
            # Post experience in thread
            embed = discord.Embed(
                title=f"Experience by {user.name}",
                description=experience.feedback,
                color=discord.Color.green()
            )
            embed.add_field(name="Rating", value="⭐" * experience.rating)
            
            if experience.photos:
                embed.add_field(name="Photos", value="\n".join(experience.photos))
                
            await thread.send(embed=embed)
            
        return {**experience_data, "experience_id": experience_id}
        
    except Exception as e:
        logger.error(f"Error creating experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{experience_id}", response_model=ExperienceResponse)
async def get_experience(experience_id: str):
    """Get experience details"""
    if experience_id not in bot.experiences:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {**bot.experiences[experience_id], "experience_id": experience_id}

@router.get("/event/{message_id}", response_model=List[ExperienceResponse])
async def get_event_experiences(message_id: int):
    """Get all experiences for an event"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    event_experiences = [
        {**exp, "experience_id": exp_id}
        for exp_id, exp in bot.experiences.items()
        if exp["message_id"] == message_id
    ]
    
    return event_experiences

@router.get("/user/{user_id}", response_model=List[ExperienceResponse])
async def get_user_experiences(user_id: int):
    """Get all experiences by a user"""
    user_experiences = [
        {**exp, "experience_id": exp_id}
        for exp_id, exp in bot.experiences.items()
        if exp["user_id"] == user_id
    ]
    
    return user_experiences

@router.get("/event/{message_id}/stats")
async def get_event_stats(message_id: int):
    """Get statistics for an event's experiences"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    event_experiences = [
        exp for exp in bot.experiences.values()
        if exp["message_id"] == message_id
    ]
    
    if not event_experiences:
        return {
            "total_experiences": 0,
            "average_rating": 0,
            "rating_distribution": {i: 0 for i in range(1, 6)}
        }
        
    total_ratings = sum(exp["rating"] for exp in event_experiences)
    rating_distribution = {i: 0 for i in range(1, 6)}
    
    for exp in event_experiences:
        rating_distribution[exp["rating"]] += 1
        
    return {
        "total_experiences": len(event_experiences),
        "average_rating": total_ratings / len(event_experiences),
        "rating_distribution": rating_distribution
    } 