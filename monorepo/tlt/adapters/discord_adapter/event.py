from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import discord
from tlt.adapters.discord_adapter.bot_manager import bot
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EventCreate(BaseModel):
    topic: str
    location: str
    time: str
    creator_id: int
    guild_id: int
    channel_id: int

class EventResponse(BaseModel):
    message_id: int
    topic: str
    location: str
    time: str
    creator_id: int
    guild_id: int
    channel_id: int
    reactions: Dict[str, List[int]]

@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate):
    """Create a new event via API"""
    try:
        guild = bot.get_guild(event.guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        if not bot.is_guild_registered(event.guild_id):
            raise HTTPException(status_code=403, detail="Guild not registered for TLT events")
            
        channel = guild.get_channel(event.channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
            
        # Create embed for the event
        embed = discord.Embed(
            title=f"📅 {event.topic}",
            description=f"**📍 Location:** {event.location}\n**🕐 Time:** {event.time}",
            color=discord.Color.blue()
        )
        
        # Add creator info
        creator = guild.get_member(event.creator_id)
        if creator:
            embed.set_footer(text=f"Created by {creator.display_name}")
        
        # Send message
        message = await channel.send(embed=embed)
        
        # Store event in bot's centralized storage
        event_data = {
            "topic": event.topic,
            "location": event.location,
            "time": event.time,
            "creator_id": event.creator_id,
            "guild_id": event.guild_id,
            "channel_id": event.channel_id,
            "reactions": {},
            "created_at": discord.utils.utcnow()
        }
        bot.active_events[message.id] = event_data
        
        # Add default reactions
        default_reactions = ["✅", "❌", "❓"]
        for emoji in default_reactions:
            await message.add_reaction(emoji)
            
        # Create thread
        thread = await message.create_thread(
            name=f"RSVP: {event.topic}",
            auto_archive_duration=10080  # 7 days
        )
        bot.event_threads[message.id] = thread.id
        
        # Send thread rules
        rules_embed = discord.Embed(
            title="🔹 Thread Rules",
            description="This thread is for **EMOJI REACTIONS ONLY**.\n\n" +
                       "✅ = Attending\n❌ = Not Attending\n❓ = Maybe\n\n" +
                       "**No discussion allowed.** Messages will be deleted.",
            color=discord.Color.yellow()
        )
        await thread.send(embed=rules_embed)
        
        # Schedule automatic reminders
        await bot.schedule_event_reminders(message.id, event.time)
            
        return {**event_data, "message_id": message.id}
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{message_id}", response_model=EventResponse)
async def get_event(message_id: int):
    """Get event details"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
    return {**bot.active_events[message_id], "message_id": message_id}

@router.get("/", response_model=List[EventResponse])
async def list_events():
    """List all active events"""
    return [{**event, "message_id": msg_id} for msg_id, event in bot.active_events.items()]

@router.delete("/{message_id}")
async def delete_event(message_id: int):
    """Delete an event"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        event = bot.active_events[message_id]
        guild = bot.get_guild(event["guild_id"])
        if guild:
            channel = guild.get_channel(event["channel_id"])
            if channel:
                message = await channel.fetch_message(message_id)
                await message.delete()
                
        del bot.active_events[message_id]
        if message_id in bot.event_threads:
            del bot.event_threads[message_id]
            
        # Remove related reminders
        reminders_to_remove = [r_id for r_id, reminder in bot.active_reminders.items() 
                             if reminder.get("message_id") == message_id]
        for r_id in reminders_to_remove:
            del bot.active_reminders[r_id]
            
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{message_id}", response_model=EventResponse)
async def update_event(message_id: int, event: EventCreate):
    """Update an event"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        guild = bot.get_guild(event.guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        channel = guild.get_channel(event.channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
            
        message = await channel.fetch_message(message_id)
        
        # Update embed
        embed = discord.Embed(
            title=f"📅 {event.topic} (Updated)",
            description=f"**📍 Location:** {event.location}\n**🕐 Time:** {event.time}",
            color=discord.Color.green()
        )
        
        creator = guild.get_member(event.creator_id)
        if creator:
            embed.set_footer(text=f"Updated by {creator.display_name}")
            
        await message.edit(embed=embed)
        
        # Update stored event
        stored_event = bot.active_events[message_id]
        stored_event.update({
            "topic": event.topic,
            "location": event.location,
            "time": event.time,
            "creator_id": event.creator_id,
            "guild_id": event.guild_id,
            "channel_id": event.channel_id
        })
        
        return {**stored_event, "message_id": message_id}
        
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 