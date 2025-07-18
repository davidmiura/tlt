from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import discord
from tlt.adapters.discord_adapter.bot_manager import bot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
router = APIRouter()

class ReminderCreate(BaseModel):
    message_id: int
    user_id: int
    reminder_time: datetime
    message: str

class ReminderResponse(BaseModel):
    reminder_id: str
    message_id: int
    user_id: int
    reminder_time: datetime
    message: str
    status: str

@router.post("/", response_model=ReminderResponse)
async def create_reminder(reminder: ReminderCreate):
    """Create a new reminder"""
    if reminder.message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        event = bot.active_events[reminder.message_id]
        guild = bot.get_guild(event["guild_id"])
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        user = guild.get_member(reminder.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Create reminder ID
        reminder_id = f"{reminder.message_id}_{reminder.user_id}_{int(reminder.reminder_time.timestamp())}"
        
        # Store reminder
        reminder_data = {
            "message_id": reminder.message_id,
            "user_id": reminder.user_id,
            "reminder_time": reminder.reminder_time,
            "message": reminder.message,
            "status": "pending"
        }
        bot.active_reminders[reminder_id] = reminder_data
        
        # Schedule reminder
        asyncio.create_task(schedule_reminder(reminder_id))
        
        return {**reminder_data, "reminder_id": reminder_id}
        
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def schedule_reminder(reminder_id: str):
    """Schedule a reminder to be sent"""
    reminder = bot.active_reminders[reminder_id]
    event = bot.active_events[reminder["message_id"]]
    
    # Calculate delay until reminder time
    now = datetime.now(timezone.utc)
    delay = (reminder["reminder_time"] - now).total_seconds()
    
    if delay > 0:
        await asyncio.sleep(delay)
        
    try:
        guild = bot.get_guild(event["guild_id"])
        if not guild:
            logger.error(f"Guild not found for reminder {reminder_id}")
            return
            
        user = guild.get_member(reminder["user_id"])
        if not user:
            logger.error(f"User not found for reminder {reminder_id}")
            return
            
        # Send reminder DM
        embed = discord.Embed(
            title="Event Reminder",
            description=reminder["message"],
            color=discord.Color.blue()
        )
        embed.add_field(name="Event", value=event["topic"])
        embed.add_field(name="Location", value=event["location"])
        embed.add_field(name="Time", value=event["time"])
        
        await user.send(embed=embed)
        
        # Update reminder status
        reminder["status"] = "sent"
        
    except Exception as e:
        logger.error(f"Error sending reminder {reminder_id}: {e}")
        reminder["status"] = "failed"

@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str):
    """Get reminder details"""
    if reminder_id not in bot.active_reminders:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {**bot.active_reminders[reminder_id], "reminder_id": reminder_id}

@router.get("/", response_model=List[ReminderResponse])
async def list_reminders():
    """List all active reminders"""
    return [{**reminder, "reminder_id": reminder_id} 
            for reminder_id, reminder in bot.active_reminders.items()]

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """Delete a reminder"""
    if reminder_id not in bot.active_reminders:
        raise HTTPException(status_code=404, detail="Reminder not found")
        
    del bot.active_reminders[reminder_id]
    return {"status": "success"}

@router.post("/{message_id}/thread")
async def create_thread(message_id: int, content: str):
    """Create a thread for an event"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        event = bot.active_events[message_id]
        guild = bot.get_guild(event["guild_id"])
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        channel = guild.get_channel(event["channel_id"])
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
            
        message = await channel.fetch_message(message_id)
        
        # Create thread
        thread = await message.create_thread(
            name=f"Discussion: {event['topic']}",
            auto_archive_duration=1440  # 24 hours
        )
        
        # Send initial message
        await thread.send(content)
        
        return {"thread_id": thread.id}
        
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 