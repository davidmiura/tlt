import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventUpdateModal(discord.ui.Modal, title="🔄 Update Event Vibes 🔄"):
    def __init__(self, bot_instance: 'DiscordBot', message_id: int, event: dict):
        super().__init__()
        self.bot_instance = bot_instance
        self.message_id = message_id
        self.event = event
        
        # Pre-populate fields with current values
        self.topic.default = event.get("topic", "")
        self.location.default = event.get("location", "")
        self.time.default = event.get("time", "")
    
    topic = discord.ui.TextInput(
        label="🎯 Event Topic/Title",
        placeholder="Change the vibe? What's the new energy? ⚡",
        required=True,
        max_length=100
    )
    
    location = discord.ui.TextInput(
        label="📍 Location",
        placeholder="New spot? Same energy, different place? 🌟",
        required=True,
        max_length=200
    )
    
    time = discord.ui.TextInput(
        label="⏰ Time",
        placeholder="Time shift? When's the new move happening? 🚀",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from tlt.adapters.discord_adapter.commands.tlt.update.handler import EventUpdateHandler
        handler = EventUpdateHandler(self.bot_instance)
        await handler.handle_modal_submission(
            interaction, 
            self.message_id,
            self.topic.value, 
            self.location.value, 
            self.time.value
        )