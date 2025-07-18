import discord
from typing import TYPE_CHECKING
from datetime import datetime
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventUpdateHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        # Get events for this guild that the user can update
        guild_events = []
        for msg_id, event in self.bot_instance.active_events.items():
            if (event.get("guild_id") == interaction.guild.id and 
                (event["creator_id"] == interaction.user.id or self.bot_instance.is_admin(interaction.user))):
                guild_events.append((msg_id, event))
        
        # Sort by creation time (most recent first) - this represents "upcoming" events
        guild_events.sort(key=lambda x: x[1].get("created_at", datetime.min), reverse=True)
        
        if not guild_events:
            await interaction.response.send_message(
                "😅 No events to update rn! You can only edit your own events (unless you're admin ofc) 💅✨", 
                ephemeral=True
            )
            return
        
        # Create select view with top 5 events
        from tlt.adapters.discord_adapter.commands.tlt.update.view import EventSelectView
        view = EventSelectView(self.bot_instance, guild_events)
        
        embed = discord.Embed(
            title="🔥 Time to Switch Things Up! 🔥",
            description="Ready to update your event? Pick one below and let's make it even better! ✨💫",
            color=discord.Color.purple()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def handle_modal_submission(self, interaction: discord.Interaction, message_id: int, topic: str, location: str, time: str):
        event = self.bot_instance.active_events[message_id]
        
        # Update event data
        event["topic"] = topic
        event["location"] = location
        event["time"] = time
        
        # Update message
        try:
            channel = interaction.guild.get_channel(event["channel_id"])
            message = await channel.fetch_message(message_id)
            
            embed = discord.Embed(
                title=f"📅 {event['topic']} (Updated)",
                description=f"**📍 Location:** {event['location']}\n**🕐 Time:** {event['time']}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Updated by {interaction.user.display_name}")
            
            await message.edit(embed=embed)
            await interaction.response.send_message("🎉 Yesss! Event updated and looking fresh! The vibes are immaculate ✨💯", ephemeral=True)
            
            # Send event update CloudEvent to TLT service for ambient agent processing
            try:
                from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
                
                # Prepare update data
                update_data = {
                    "event_data": {
                        "topic": event["topic"],
                        "location": event["location"],
                        "time": event["time"],
                        "message_id": str(message_id),
                        "updated_by": interaction.user.id,
                        "updated_at": datetime.now().isoformat()
                    },
                    "interaction_data": {
                        "user_id": str(interaction.user.id),
                        "user_name": interaction.user.display_name,
                        "guild_id": str(interaction.guild.id),
                        "guild_name": interaction.guild.name,
                        "channel_id": str(interaction.channel.id),
                        "channel_name": interaction.channel.name,
                        "command": "update_event",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Send CloudEvent to TLT service
                cloudevent_id = await tlt_client.send_event_update(
                    event_id=str(message_id),
                    update_type="event_updated",
                    data=update_data,
                    guild_id=str(interaction.guild.id),
                    channel_id=str(interaction.channel.id),
                    user_id=str(interaction.user.id),
                    priority="normal",
                    metadata={
                        "source": "discord_update_command",
                        "action": "event_updated",
                        "original_topic": event.get("topic", "Unknown"),
                        "updated_fields": ["topic", "location", "time"]
                    }
                )
                
                if cloudevent_id:
                    logger.info(f"Event update CloudEvent sent to TLT service, id: {cloudevent_id}")
                else:
                    logger.warning("Failed to send event update CloudEvent to TLT service")
                    
            except Exception as tlt_e:
                logger.error(f"Error sending event update CloudEvent to TLT service: {tlt_e}")
                # Don't fail the command if TLT service is unavailable
            
        except discord.NotFound:
            await interaction.response.send_message("😵 Oops! Can't find that event message anymore... it might've been deleted 👻", ephemeral=True)
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            await interaction.response.send_message("😬 Something went wrong updating your event... try again bestie! 🔄", ephemeral=True)