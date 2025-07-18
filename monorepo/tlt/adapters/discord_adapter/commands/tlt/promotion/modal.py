import discord
from typing import List, Tuple, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventSelectDropdown(discord.ui.Select):
    """Dropdown for selecting an event"""
    
    def __init__(self, events: List[Tuple[str, str]], bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
        
        # Create options from events
        options = []
        for event_id, event_title in events[:25]:  # Discord limit
            options.append(discord.SelectOption(
                label=event_title[:100],  # Discord limit
                description=f"Event ID: {event_id}",
                value=event_id
            ))
        
        super().__init__(
            placeholder="Choose an event for promotion setup...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Store the selected event ID in the view
        self.view.selected_event_id = self.values[0]
        
        # Update the button to show which event was selected
        for child in self.view.children:
            if isinstance(child, ImageUploadButton):
                child.disabled = False
                break
        
        # Get event data for display
        event_message_id = int(self.values[0])
        event_data = self.bot_instance.active_events.get(event_message_id, {})
        event_title = event_data.get("topic", f"Event {self.values[0]}")
        
        embed = discord.Embed(
            title="📸 Event Selected",
            description=f"**{event_title}** selected for promotion setup!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Next Step",
            value="Click the **Upload Image** button below to add a promotional image for this event.",
            inline=False
        )
        embed.set_footer(text=f"Selected by {interaction.user.display_name}")
        
        await interaction.response.edit_message(embed=embed, view=self.view)

class ImageUploadButton(discord.ui.Button):
    """Button to trigger image upload modal"""
    
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
        super().__init__(
            label="Upload Image",
            style=discord.ButtonStyle.primary,
            emoji="📸",
            disabled=True  # Disabled until event is selected
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Show the image upload modal
        modal = ImageUploadModal(self.bot_instance, self.view.selected_event_id)
        await interaction.response.send_modal(modal)

class ImageUploadModal(discord.ui.Modal):
    """Modal for image upload instructions"""
    
    def __init__(self, bot_instance: 'DiscordBot', event_id: str):
        self.bot_instance = bot_instance
        self.event_id = event_id
        super().__init__(title="📸 Upload Promotion Image")
        
        # Add a text input for image URL or instructions
        self.image_instructions = discord.ui.TextInput(
            label="Image Upload Instructions",
            placeholder="Please attach an image to your next message in this channel after submitting this modal...",
            style=discord.TextStyle.paragraph,
            default=(
                "After submitting this modal, please send a message in this channel with your promotional image attached. "
                "The bot will automatically detect and process your image upload for the selected event."
            ),
            max_length=500,
            required=False
        )
        self.add_item(self.image_instructions)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        try:
            # Get event data for display
            event_message_id = int(self.event_id)
            event_data = self.bot_instance.active_events.get(event_message_id, {})
            event_title = event_data.get("topic", f"Event {self.event_id}")
            
            embed = discord.Embed(
                title="📸 Ready for Image Upload",
                description=f"**{event_title}** is ready for promotional image upload!",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="📋 Instructions",
                value=(
                    "1. **Send a message** in this channel with your promotional image attached\n"
                    "2. **Include the text** `!promotion-upload` in your message\n"
                    "3. **Bot will automatically** detect and process your image\n"
                    "4. **Image will be saved** to the promotion directory for this event"
                ),
                inline=False
            )
            embed.add_field(
                name="📝 Supported Formats",
                value="JPG, PNG, GIF, WEBP (max 8MB)",
                inline=True
            )
            embed.add_field(
                name="📁 Storage Location",
                value=f"`guild_data/data/{interaction.guild.id}/promotion/{interaction.user.id}/`",
                inline=True
            )
            embed.set_footer(text=f"Waiting for upload from {interaction.user.display_name}")
            
            # Store the pending upload info
            if not hasattr(self.bot_instance, 'pending_promotion_uploads'):
                self.bot_instance.pending_promotion_uploads = {}
            
            self.bot_instance.pending_promotion_uploads[interaction.user.id] = {
                'event_id': self.event_id,
                'guild_id': interaction.guild.id,
                'channel_id': interaction.channel.id,
                'event_title': event_title
            }
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in promotion image upload modal: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while setting up image upload.",
                ephemeral=True
            )

class PromotionMediaModal(discord.ui.View):
    """Main view for promotion media setup"""
    
    def __init__(self, bot_instance: 'DiscordBot', events: List[Tuple[str, str]]):
        super().__init__(timeout=300)
        self.bot_instance = bot_instance
        self.selected_event_id = None
        
        # Add event selection dropdown
        self.add_item(EventSelectDropdown(events, bot_instance))
        
        # Add image upload button
        self.add_item(ImageUploadButton(bot_instance))
    
    async def on_timeout(self):
        """Called when the view times out"""
        # Disable all items
        for item in self.children:
            item.disabled = True