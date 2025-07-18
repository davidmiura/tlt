import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventSelectView(discord.ui.View):
    def __init__(self, bot_instance: 'DiscordBot', events: list):
        super().__init__(timeout=60)
        self.bot_instance = bot_instance
        self.events = events
        
        # Create select menu with events
        options = []
        for msg_id, event in events[:5]:  # Top 5 events
            # Truncate long titles for display
            display_title = event["topic"][:50] + "..." if len(event["topic"]) > 50 else event["topic"]
            description = f"📍 {event['location']} • 🕐 {event['time']}"[:100]
            
            options.append(discord.SelectOption(
                label=display_title,
                description=description,
                value=str(msg_id)
            ))
        
        if options:
            self.select_menu = discord.ui.Select(
                placeholder="⚠️ Choose the event to delete (can't be undone!) 🗑️",
                options=options
            )
            self.select_menu.callback = self.select_callback
            self.add_item(self.select_menu)
    
    async def select_callback(self, interaction: discord.Interaction):
        message_id = int(self.select_menu.values[0])
        event = self.bot_instance.active_events[message_id]
        
        # Check permissions
        if event["creator_id"] != interaction.user.id and not self.bot_instance.is_admin(interaction.user):
            await interaction.response.send_message("🚫 Nah bestie, that's not your event to delete! Only the creator (or admin) can delete this ✋😤", ephemeral=True)
            return
        
        # Show confirmation modal
        from tlt.adapters.discord_adapter.commands.tlt.delete.confirmation_modal import DeleteConfirmationModal
        modal = DeleteConfirmationModal(self.bot_instance, message_id, event)
        await interaction.response.send_modal(modal)