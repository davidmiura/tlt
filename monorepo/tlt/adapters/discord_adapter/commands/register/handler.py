import discord
from typing import TYPE_CHECKING
import logging
from datetime import datetime

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class RegisterCommandHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_command(self, interaction: discord.Interaction):
        """Handle guild registration"""
        if not self.bot_instance.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only administrators can register the guild.", ephemeral=True)
            return
            
        if self.bot_instance.is_guild_registered(interaction.guild.id):
            await interaction.response.send_message("✅ Guild is already registered for TLT events.", ephemeral=True)
            return
        
        # Send CloudEvent to TLT service for registration processing
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.register_guild(
                guild_id=str(interaction.guild.id),
                guild_name=interaction.guild.name,
                channel_id=str(interaction.channel.id),
                channel_name=interaction.channel.name,
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                metadata={
                    "source": "discord_register_command",
                    "guild_member_count": interaction.guild.member_count,
                    "guild_created_at": interaction.guild.created_at.isoformat() if interaction.guild.created_at else None,
                    "registered_at": datetime.now().isoformat()
                }
            )
            
            if cloudevent_id:
                logger.info(f"Guild registration CloudEvent sent to TLT service, id: {cloudevent_id}")
            else:
                logger.warning("Failed to send guild registration CloudEvent to TLT service")
                
        except Exception as e:
            logger.error(f"Error sending guild registration CloudEvent to TLT service: {e}")
            # Continue with local registration even if TLT service is unavailable
            
        # Perform local registration
        success = await self.bot_instance.register_guild(interaction.guild, interaction.user)
        if success:
            embed = discord.Embed(
                title="🎉 Guild Registered!",
                description=f"**{interaction.guild.name}** is now registered for TLT events.",
                color=discord.Color.green()
            )
            embed.add_field(name="Registered by", value=interaction.user.mention)
            embed.add_field(name="Next Steps", value="Use `/tlt create` to create your first event!")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to register guild.", ephemeral=True)