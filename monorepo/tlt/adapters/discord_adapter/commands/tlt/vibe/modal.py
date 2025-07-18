import discord
from typing import TYPE_CHECKING, List, Tuple
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventSelectDropdown(discord.ui.Select):
    def __init__(self, events: List[Tuple[str, str]], bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
        
        # Create options from events (event_id, event_title)
        options = []
        for event_id, event_title in events[:25]:  # Discord max 25 options
            options.append(discord.SelectOption(
                label=event_title[:100],  # Max 100 chars
                value=event_id,
                description=f"Event ID: {event_id}"[:100]
            ))
        
        if not options:
            options = [discord.SelectOption(
                label="No events available",
                value="none",
                description="Create an event first"
            )]
        
        super().__init__(
            placeholder="🎯 Choose an event...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Update parent view's selected event
        self.view.selected_event_id = self.values[0]
        await interaction.response.defer()

class VibeActionDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="📸 Generate Event Slideshow",
                value="generate_event_slideshow",
                description="Create a slideshow from approved event photos",
                emoji="📸"
            ),
            discord.SelectOption(
                label="📊 Create Vibe Snapshot",
                value="create_vibe_snapshot", 
                description="Get event vibe analysis and insights",
                emoji="📊"
            ),
            discord.SelectOption(
                label="🎨 Get Vibe Canvas Preview",
                value="get_vibe_canvas_preview",
                description="Preview the collaborative vibe canvas",
                emoji="🎨"
            ),
            discord.SelectOption(
                label="📷 Get Event Photo Summary",
                value="get_event_photo_summary",
                description="View photo submission statistics",
                emoji="📷"
            )
        ]
        
        super().__init__(
            placeholder="✨ Pick your vibe action...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Update parent view's selected action
        self.view.selected_action = self.values[0]
        await interaction.response.defer()

class VibeModal(discord.ui.View):
    def __init__(self, bot_instance: 'DiscordBot', events: List[Tuple[str, str]]):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot_instance = bot_instance
        self.selected_event_id = None
        self.selected_action = None
        
        # Add dropdowns
        self.add_item(EventSelectDropdown(events, bot_instance))
        self.add_item(VibeActionDropdown())
    
    @discord.ui.button(label="🚀 Submit", style=discord.ButtonStyle.primary, emoji="🚀")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_event_id or not self.selected_action:
            await interaction.response.send_message(
                "❌ Please select both an event and an action before submitting!",
                ephemeral=True
            )
            return
        
        if self.selected_event_id == "none":
            await interaction.response.send_message(
                "❌ No events available. Create an event first using `/tlt create`!",
                ephemeral=True
            )
            return
        
        # Handle the submission
        from tlt.adapters.discord_adapter.commands.tlt.vibe.handler import VibeHandler
        handler = VibeHandler(self.bot_instance)
        await handler.handle_vibe_submission(
            interaction,
            self.selected_event_id,
            self.selected_action
        )
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Vibe action cancelled!", ephemeral=True)
        self.stop()