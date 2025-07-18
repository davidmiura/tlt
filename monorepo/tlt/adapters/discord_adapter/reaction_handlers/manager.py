import discord
from typing import Dict, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class ReactionManager:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction additions"""
        if user.bot:
            return
            
        message_id = reaction.message.id
        if message_id not in self.bot_instance.active_events:
            return
            
        event = self.bot_instance.active_events[message_id]
        emoji = str(reaction.emoji)
        
        # Initialize reactions if needed
        if "reactions" not in event:
            event["reactions"] = {}
        if emoji not in event["reactions"]:
            event["reactions"][emoji] = []
            
        # Add user if not already in list
        if user.id not in event["reactions"][emoji]:
            event["reactions"][emoji].append(user.id)
            logger.info(f'User {user.name} reacted with {emoji} to event: {event["topic"]}')
            
            # Send RSVP CloudEvent to TLT service
            await self.send_rsvp_cloudevent(reaction.message, event, user, emoji, "add")
            
        # Update message embed
        await self.update_event_embed(reaction.message, event)
    
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction removals"""
        if user.bot:
            return
            
        message_id = reaction.message.id
        if message_id not in self.bot_instance.active_events:
            return
            
        event = self.bot_instance.active_events[message_id]
        emoji = str(reaction.emoji)
        
        # Remove user from reaction list
        if "reactions" in event and emoji in event["reactions"]:
            if user.id in event["reactions"][emoji]:
                event["reactions"][emoji].remove(user.id)
                logger.info(f'User {user.name} removed {emoji} reaction from event: {event["topic"]}')
                
                # Send RSVP CloudEvent to TLT service
                await self.send_rsvp_cloudevent(reaction.message, event, user, emoji, "remove")
                
        # Update message embed  
        await self.update_event_embed(reaction.message, event)
    
    async def update_event_embed(self, message: discord.Message, event: Dict):
        """Update event message embed with current reactions"""
        embed = discord.Embed(
            title=f"📅 {event['topic']}",
            description=f"**📍 Location:** {event['location']}\n**🕐 Time:** {event['time']}",
            color=discord.Color.blue()
        )
        
        # Add reaction counts
        reactions = event.get("reactions", {})
        if reactions:
            rsvp_text = ""
            for emoji, users in reactions.items():
                if users:
                    rsvp_text += f"{emoji} {len(users)} "
            if rsvp_text:
                embed.add_field(name="📝 RSVPs", value=rsvp_text.strip(), inline=False)
                
        creator = message.guild.get_member(event["creator_id"])
        if creator:
            embed.set_footer(text=f"Created by {creator.display_name}")
            
        try:
            await message.edit(embed=embed)
        except Exception as e:
            logger.error(f"Error updating embed: {e}")
    
    async def send_rsvp_cloudevent(self, message: discord.Message, event: Dict, user: discord.Member, emoji: str, action: str):
        """Send RSVP CloudEvent to TLT service"""
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            # Prepare enhanced metadata with RSVP details
            metadata = {
                "source": "discord_rsvp_reaction",
                "rsvp_action": action,
                "emoji": emoji,
                "event_topic": event.get("topic", "Unknown"),
                "event_creator_id": str(event.get("creator_id", "Unknown")),
                "event_location": event.get("location", "Unknown"),
                "event_time": event.get("time", "Unknown"),
                "timestamp": message.created_at.isoformat(),
                "guild_id": str(message.guild.id) if message.guild else "Unknown",
                "guild_name": message.guild.name if message.guild else "Unknown",
                "channel_name": message.channel.name if hasattr(message.channel, 'name') else "Unknown"
            }
            
            # Send proper RSVP CloudEvent using the new method
            cloudevent_id = await tlt_client.send_rsvp_event(
                guild_id=str(message.guild.id),
                channel_id=str(message.channel.id),
                event_id=str(message.id),
                user_id=str(user.id),
                user_name=user.display_name,
                rsvp_type=action,  # "add" or "remove"
                action=action,
                emoji=emoji,
                metadata=metadata
            )
            
            if cloudevent_id:
                logger.info(f"RSVP {action} CloudEvent sent to TLT service, id: {cloudevent_id}")
            else:
                logger.warning(f"Failed to send RSVP {action} CloudEvent to TLT service")
                
        except Exception as e:
            logger.error(f"Error sending RSVP {action} CloudEvent to TLT service: {e}")
            # Don't fail the reaction if TLT service is unavailable