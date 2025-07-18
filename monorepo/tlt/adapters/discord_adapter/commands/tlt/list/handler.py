import discord
from typing import TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventListHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        # Get local events first
        guild_events = [
            (msg_id, event) for msg_id, event in self.bot_instance.active_events.items()
            if event.get("guild_id") == interaction.guild.id
        ]
        
        # Send CloudEvent to TLT service for list events processing
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            # Prepare enhanced metadata with event summary
            events_summary = [{
                "message_id": msg_id,
                "topic": event["topic"],
                "location": event["location"],
                "time": event["time"],
                "creator_id": event["creator_id"],
                "reaction_count": sum(len(users) for users in event.get("reactions", {}).values())
            } for msg_id, event in guild_events[:10]]
            
            cloudevent_id = await tlt_client.list_events(
                guild_id=str(interaction.guild.id),
                channel_id=str(interaction.channel.id),
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                metadata={
                    "source": "discord_list_command",
                    "total_events": len(guild_events),
                    "events_displayed": min(len(guild_events), 10),
                    "events_summary": events_summary
                }
            )
            
            if cloudevent_id:
                logger.info(f"List events CloudEvent sent to TLT service, id: {cloudevent_id}")
            else:
                logger.warning("Failed to send list events CloudEvent to TLT service")
                
        except Exception as e:
            logger.error(f"Error sending list events CloudEvent to TLT service: {e}")
            # Continue with local list even if TLT service is unavailable
        
        if not guild_events:
            await interaction.response.send_message("📭 No active events in this guild.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📋 Active Events",
            color=discord.Color.blue()
        )
        
        for msg_id, event in guild_events[:10]:  # Limit to 10 events
            reactions_text = ""
            for emoji, users in event.get("reactions", {}).items():
                if users:
                    reactions_text += f"{emoji} {len(users)} "
            
            embed.add_field(
                name=f"{event['topic']}",
                value=f"📍 {event['location']}\n🕐 {event['time']}\n{reactions_text or 'No RSVPs yet'}\n`ID: {msg_id}`",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)