import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventBridgeHandlers:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def create_event_from_modal(self, interaction: discord.Interaction, topic: str, location: str, time: str):
        """Create a new event from modal submission"""
        from tlt.adapters.discord_adapter.commands.tlt.create.handler import EventCreateHandler
        handler = EventCreateHandler(self.bot_instance)
        await handler.handle_modal_submission(interaction, topic, location, time)
    
    async def update_event_from_modal(self, interaction: discord.Interaction, message_id: int, topic: str, location: str, time: str):
        """Update an existing event from modal submission"""
        from tlt.adapters.discord_adapter.commands.tlt.update.handler import EventUpdateHandler
        handler = EventUpdateHandler(self.bot_instance)
        await handler.handle_modal_submission(interaction, message_id, topic, location, time)