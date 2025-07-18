import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class SlashCommandSetup:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def setup_slash_commands(self):
        """Setup slash commands"""
        from tlt.adapters.discord_adapter.commands.register.handler import RegisterCommandHandler
        from tlt.adapters.discord_adapter.commands.deregister.handler import DeregisterCommandHandler
        from tlt.adapters.discord_adapter.slash_commands.router import TLTCommandRouter
        
        router = TLTCommandRouter(self.bot_instance)
        
        @self.bot_instance.tree.command(name="tlt", description="Manage TLT events")
        @discord.app_commands.describe(
            action="Action to perform"
        )
        async def tlt_command(
            interaction: discord.Interaction,
            action: str
        ):
            await router.handle_tlt_command(interaction, action, None)
            
        @self.bot_instance.tree.command(name="register", description="Register guild for TLT events (Admin only)")
        async def register_command(interaction: discord.Interaction):
            handler = RegisterCommandHandler(self.bot_instance)
            await handler.handle_command(interaction)
            
        @self.bot_instance.tree.command(name="deregister", description="Deregister guild from TLT events (Admin only)")
        async def deregister_command(interaction: discord.Interaction):
            handler = DeregisterCommandHandler(self.bot_instance)
            await handler.handle_command(interaction)