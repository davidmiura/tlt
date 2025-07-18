import discord
from typing import TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventInfoHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        # Get events for this guild
        guild_events = []
        for msg_id, event in self.bot_instance.active_events.items():
            if event.get("guild_id") == interaction.guild.id:
                guild_events.append((msg_id, event))
        
        # Sort by creation time (most recent first)
        guild_events.sort(key=lambda x: x[1].get("created_at", datetime.min), reverse=True)
        
        if not guild_events:
            await interaction.response.send_message(
                "😅 No events found! Create some events first to see their info 💅✨", 
                ephemeral=True
            )
            return
        
        # Create select view with events
        from tlt.adapters.discord_adapter.commands.tlt.info.view import EventSelectView
        view = EventSelectView(self.bot_instance, guild_events)
        
        embed = discord.Embed(
            title="📊 Event Info Central! 📊",
            description="Want the tea on an event? Pick one below to get all the deets! ☕✨",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def handle_info_display(self, interaction: discord.Interaction, message_id: int):
        """Handle the actual info display after user selects an event"""
        if message_id not in self.bot_instance.active_events:
            await interaction.response.send_message("❌ Event not found.", ephemeral=True)
            return
        
            
        event = self.bot_instance.active_events[message_id]
        
        embed = discord.Embed(
            title=f"📊 Event Details: {event['topic']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="📍 Location", value=event['location'], inline=True)
        embed.add_field(name="🕐 Time", value=event['time'], inline=True)
        embed.add_field(name="🆔 Event ID", value=str(message_id), inline=True)
        
        creator = interaction.guild.get_member(event['creator_id'])
        embed.add_field(name="👤 Creator", value=creator.mention if creator else "Unknown", inline=True)
        embed.add_field(name="📅 Created", value=event['created_at'].strftime("%Y-%m-%d %H:%M UTC"), inline=True)
        
        # RSVP summary
        reactions = event.get('reactions', {})
        rsvp_text = ""
        for emoji, users in reactions.items():
            if users:
                rsvp_text += f"{emoji} {len(users)} users\n"
        
        if rsvp_text:
            embed.add_field(name="📝 RSVPs", value=rsvp_text, inline=False)
        else:
            embed.add_field(name="📝 RSVPs", value="No RSVPs yet", inline=False)
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send event info CloudEvent to TLT service for ambient agent processing
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.get_event_info(
                guild_id=str(interaction.guild.id),
                channel_id=str(interaction.channel.id),
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                event_id=str(message_id),
                metadata={
                    "source": "discord_info_command",
                    "event_topic": event.get("topic", "Unknown"),
                    "event_creator_id": str(event.get("creator_id", "Unknown")),
                    "rsvp_summary": {
                        emoji: len(users) for emoji, users in event.get('reactions', {}).items()
                    },
                    "total_rsvps": sum(len(users) for users in event.get('reactions', {}).values())
                }
            )
            
            if cloudevent_id:
                logger.info(f"Event info CloudEvent sent to TLT service, id: {cloudevent_id}")
            else:
                logger.warning("Failed to send event info CloudEvent to TLT service")
                
        except Exception as e:
            logger.error(f"Error sending event info CloudEvent to TLT service: {e}")
            # Don't fail the command if TLT service is unavailable