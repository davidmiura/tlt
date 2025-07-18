from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import discord
from tlt.adapters.discord_adapter.bot_manager import bot
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ReactionUpdate(BaseModel):
    message_id: int
    emoji: str
    user_id: int
    action: str  # "add" or "remove"

@router.post("/reaction")
async def handle_reaction(reaction: ReactionUpdate):
    """Handle reaction updates"""
    if reaction.message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    try:
        event = bot.active_events[reaction.message_id]
        guild = bot.get_guild(event["guild_id"])
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
            
        channel = guild.get_channel(event["channel_id"])
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
            
        message = await channel.fetch_message(reaction.message_id)
        user = guild.get_member(reaction.user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Initialize reactions dictionary if it doesn't exist
        if "reactions" not in event:
            event["reactions"] = {}
            
        # Initialize emoji list if it doesn't exist
        if reaction.emoji not in event["reactions"]:
            event["reactions"][reaction.emoji] = []
            
        if reaction.action == "add":
            if reaction.user_id not in event["reactions"][reaction.emoji]:
                event["reactions"][reaction.emoji].append(reaction.user_id)
                logger.info(f'User {user.name} reacted with {reaction.emoji} to event: {event["topic"]}')
        else:  # remove
            if reaction.user_id in event["reactions"][reaction.emoji]:
                event["reactions"][reaction.emoji].remove(reaction.user_id)
                logger.info(f'User {user.name} removed {reaction.emoji} reaction from event: {event["topic"]}')
                
        # Update the message embed
        await update_event_message(message, event)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling reaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def update_event_message(message: discord.Message, event: Dict):
    """Update the event message with current reaction counts"""
    embed = discord.Embed(
        title=f"Event: {event['topic']}",
        description=f"Location: {event['location']}\nTime: {event['time']}",
        color=discord.Color.blue()
    )
    
    # Add reaction counts to the embed
    if "reactions" in event:
        reaction_text = "**Reactions:**\n"
        for emoji, users in event["reactions"].items():
            if users:  # Only show reactions that have users
                reaction_text += f"{emoji}: {len(users)} users\n"
        embed.add_field(name="Responses", value=reaction_text, inline=False)
    
    # Add the event creator
    guild = message.guild
    creator = guild.get_member(event["creator_id"])
    if creator:
        embed.set_footer(text=f"Created by {creator.name}")
    
    # Update the message
    await message.edit(embed=embed)

@router.get("/{message_id}/reactions")
async def get_reactions(message_id: int):
    """Get all reactions for an event"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    event = bot.active_events[message_id]
    return event.get("reactions", {})

@router.get("/{message_id}/reactions/{emoji}")
async def get_reaction_users(message_id: int, emoji: str):
    """Get users who reacted with a specific emoji"""
    if message_id not in bot.active_events:
        raise HTTPException(status_code=404, detail="Event not found")
        
    event = bot.active_events[message_id]
    reactions = event.get("reactions", {})
    
    if emoji not in reactions:
        return []
        
    return reactions[emoji] 