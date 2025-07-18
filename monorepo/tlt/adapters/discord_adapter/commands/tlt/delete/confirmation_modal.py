import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class DeleteConfirmationModal(discord.ui.Modal):
    def __init__(self, bot_instance: 'DiscordBot', message_id: int, event: dict):
        super().__init__(title="🗑️ Confirm Event Deletion")
        self.bot_instance = bot_instance
        self.message_id = message_id
        self.event = event
        
        # Confirmation input
        self.confirm_input = discord.ui.TextInput(
            label="Type 'DELETE' to confirm",
            placeholder="Type DELETE to confirm deletion",
            required=True,
            max_length=10
        )
        
        self.add_item(self.confirm_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Check confirmation
        if self.confirm_input.value.upper() != "DELETE":
            await interaction.response.send_message(
                "❌ Confirmation failed. Event deletion cancelled. Type 'DELETE' exactly to confirm.", 
                ephemeral=True
            )
            return
        
        # Delegate to the handler
        from tlt.adapters.discord_adapter.commands.tlt.delete.handler import EventDeleteHandler
        handler = EventDeleteHandler(self.bot_instance)
        await handler.handle_delete_confirmation(interaction, self.message_id)