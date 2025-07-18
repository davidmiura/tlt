import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class TLTCommandRouter:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_tlt_command(self, interaction: discord.Interaction, action: str, event_id: str):
        """Handle /tlt command"""
        if not self.bot_instance.guild_manager.is_guild_registered(interaction.guild.id):
            await interaction.response.send_message("❌ Guild not registered. Use `/register` first.", ephemeral=True)
            return
            
        action = action.lower()
        
        if action == "create":
            # Show modal for event creation
            from tlt.adapters.discord_adapter.commands.tlt.create.modal import EventCreateModal
            modal = EventCreateModal(self.bot_instance)
            await interaction.response.send_modal(modal)
        elif action == "list":
            logger.debug(f"Listing events for guild list_events_command **interaction** {interaction}")
            from tlt.adapters.discord_adapter.commands.tlt.list.handler import EventListHandler
            handler = EventListHandler(self.bot_instance)
            await handler.handle_command(interaction)
        elif action == "update":
            from tlt.adapters.discord_adapter.commands.tlt.update.handler import EventUpdateHandler
            handler = EventUpdateHandler(self.bot_instance)
            await handler.handle_command(interaction)
        elif action == "delete":
            from tlt.adapters.discord_adapter.commands.tlt.delete.handler import EventDeleteHandler
            handler = EventDeleteHandler(self.bot_instance)
            await handler.handle_command(interaction)
        elif action == "info":
            from tlt.adapters.discord_adapter.commands.tlt.info.handler import EventInfoHandler
            handler = EventInfoHandler(self.bot_instance)
            await handler.handle_command(interaction)
        elif action == "vibe":
            from tlt.adapters.discord_adapter.commands.tlt.vibe.handler import VibeHandler
            handler = VibeHandler(self.bot_instance)
            await handler.handle_vibe_command(interaction)
        elif action.startswith("promotion"):
            # Handle promotion with sub-action (e.g., "promotion media")
            parts = action.split()
            if len(parts) >= 2:
                sub_action = parts[1]
                from tlt.adapters.discord_adapter.commands.tlt.promotion.handler import PromotionHandler
                handler = PromotionHandler(self.bot_instance)
                await handler.handle_promotion_command(interaction, sub_action)
            else:
                await interaction.response.send_message(
                    "❌ Invalid promotion command. Use: `promotion media`", 
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `create`, `list`, `update`, `delete`, `info`, `vibe`, or `promotion media`", 
                ephemeral=True
            )