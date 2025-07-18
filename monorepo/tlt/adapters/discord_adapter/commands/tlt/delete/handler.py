import discord
from typing import TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventDeleteHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        # Get events for this guild that the user can delete
        guild_events = []
        for msg_id, event in self.bot_instance.active_events.items():
            if (event.get("guild_id") == interaction.guild.id and 
                (event["creator_id"] == interaction.user.id or self.bot_instance.is_admin(interaction.user))):
                guild_events.append((msg_id, event))
        
        # Sort by creation time (most recent first)
        guild_events.sort(key=lambda x: x[1].get("created_at", datetime.min), reverse=True)
        
        if not guild_events:
            await interaction.response.send_message(
                "😅 No events to delete! You can only delete your own events (unless you're admin) 💅✨", 
                ephemeral=True
            )
            return
        
        # Create select view with events
        from tlt.adapters.discord_adapter.commands.tlt.delete.view import EventSelectView
        view = EventSelectView(self.bot_instance, guild_events)
        
        embed = discord.Embed(
            title="🗑️ Time to Clean House! 🗑️",
            description="Ready to delete an event? Pick one below. This action can't be undone! 🚨⚠️",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def handle_delete_confirmation(self, interaction: discord.Interaction, message_id: int):
        """Handle the actual deletion after user confirms via select view"""
        if message_id not in self.bot_instance.active_events:
            await interaction.response.send_message("❌ Event not found.", ephemeral=True)
            return
            
        event = self.bot_instance.active_events[message_id]
        if event["creator_id"] != interaction.user.id and not self.bot_instance.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only the event creator or admins can delete events.", ephemeral=True)
            return
        
            
        # Perform local deletion
        try:
            channel = interaction.guild.get_channel(event["channel_id"])
            message = await channel.fetch_message(message_id)
            await message.delete()
            
            # Clean up
            del self.bot_instance.active_events[message_id]
            if message_id in self.bot_instance.event_threads:
                del self.bot_instance.event_threads[message_id]
                
            # Remove related reminders
            reminders_to_remove = [r_id for r_id, reminder in self.bot_instance.active_reminders.items() 
                                 if reminder.get("message_id") == message_id]
            for r_id in reminders_to_remove:
                del self.bot_instance.active_reminders[r_id]
                
            await interaction.response.send_message("✅ Event deleted successfully!", ephemeral=True)
            
            # Send event deletion CloudEvent to TLT service for ambient agent processing
            try:
                from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
                
                cloudevent_id = await tlt_client.delete_event(
                    guild_id=str(interaction.guild.id),
                    channel_id=str(interaction.channel.id),
                    user_id=str(interaction.user.id),
                    user_name=interaction.user.display_name,
                    event_id=str(message_id),
                    metadata={
                        "source": "discord_delete_command",
                        "event_topic": event.get("topic", "Unknown"),
                        "event_creator_id": str(event.get("creator_id", "Unknown")),
                        "deleted_event": event.copy(),
                        "was_creator": event["creator_id"] == interaction.user.id,
                        "reminders_removed": len(reminders_to_remove)
                    }
                )
                
                if cloudevent_id:
                    logger.info(f"Delete event CloudEvent sent to TLT service, id: {cloudevent_id}")
                else:
                    logger.warning("Failed to send delete event CloudEvent to TLT service")
                    
            except Exception as tlt_e:
                logger.error(f"Error sending delete event CloudEvent to TLT service: {tlt_e}")
                # Don't fail the command if TLT service is unavailable
            
        except discord.NotFound:
            await interaction.response.send_message("❌ Event message not found.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            await interaction.response.send_message("❌ Failed to delete event.", ephemeral=True)