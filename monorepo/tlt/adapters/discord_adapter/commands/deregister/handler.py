import discord
from typing import TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class DeregisterCommandHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        """Handle guild deregistration"""
        if not self.bot_instance.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only administrators can deregister the guild.", ephemeral=True)
            return
            
        if not self.bot_instance.is_guild_registered(interaction.guild.id):
            await interaction.response.send_message("❌ Guild is not registered for TLT events.", ephemeral=True)
            return
        
        # Send CloudEvent to TLT service for deregistration processing
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            # Count active events and reminders being cancelled
            active_events_count = len([e for e in self.bot_instance.active_events.values() 
                                     if e.get("guild_id") == interaction.guild.id])
            active_reminders_count = len([r for r in self.bot_instance.active_reminders.values() 
                                        if r.get("guild_id") == interaction.guild.id])
            
            cloudevent_id = await tlt_client.deregister_guild(
                guild_id=str(interaction.guild.id),
                guild_name=interaction.guild.name,
                channel_id=str(interaction.channel.id),
                channel_name=interaction.channel.name,
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                metadata={
                    "source": "discord_deregister_command",
                    "cancelled_events_count": active_events_count,
                    "cancelled_reminders_count": active_reminders_count,
                    "guild_member_count": interaction.guild.member_count,
                    "deregistered_at": datetime.now().isoformat(),
                    "impact": f"{active_events_count} events, {active_reminders_count} reminders cancelled"
                }
            )
            
            if cloudevent_id:
                logger.info(f"Guild deregistration CloudEvent sent to TLT service, id: {cloudevent_id}")
            else:
                logger.warning("Failed to send guild deregistration CloudEvent to TLT service")
                
        except Exception as e:
            logger.error(f"Error sending guild deregistration CloudEvent to TLT service: {e}")
            # Continue with local deregistration even if TLT service is unavailable
            
        # Perform local deregistration
        success = await self.bot_instance.deregister_guild(interaction.guild, interaction.user)
        if success:
            embed = discord.Embed(
                title="👋 Guild Deregistered",
                description=f"**{interaction.guild.name}** has been deregistered from TLT events.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Deregistered by", value=interaction.user.mention)
            embed.add_field(name="Note", value="All active events and reminders have been cancelled.")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to deregister guild.", ephemeral=True)