import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventCreateModal(discord.ui.Modal, title="✨ Create New Event ✨"):
    def __init__(self, bot_instance: 'DiscordBot'):
        super().__init__()
        self.bot_instance = bot_instance
    
    topic = discord.ui.TextInput(
        label="🎯 Topic/Title",
        placeholder="What's the vibe? Drop that event name... ✨",
        required=True,
        max_length=100
    )
    
    location = discord.ui.TextInput(
        label="📍 Location",
        placeholder="Where we meeting up? IRL or virtual? 🌍",
        required=True,
        max_length=200
    )
    
    time = discord.ui.TextInput(
        label="⏰ Time",
        placeholder="When's this happening? Be specific bestie! 📅",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from tlt.adapters.discord_adapter.commands.tlt.create.handler import EventCreateHandler
        handler = EventCreateHandler(self.bot_instance)
        await handler.handle_modal_submission(
            interaction, 
            self.topic.value, 
            self.location.value, 
            self.time.value
        )