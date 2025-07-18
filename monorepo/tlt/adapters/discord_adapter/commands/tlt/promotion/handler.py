import discord
from typing import TYPE_CHECKING, List, Tuple
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class PromotionHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    def get_available_events(self, guild_id: int) -> List[Tuple[str, str]]:
        """Get list of available events for the guild"""
        events = []
        for message_id, event_data in self.bot_instance.active_events.items():
            if event_data.get("guild_id") == guild_id:
                topic = event_data.get("topic", f"Event {message_id}")
                events.append((str(message_id), topic))
        
        return events
    
    async def handle_promotion_command(self, interaction: discord.Interaction, sub_action: str):
        """Handle the /tlt promotion command"""
        try:
            # Check if guild is registered
            if not self.bot_instance.is_guild_registered(interaction.guild.id):
                await interaction.response.send_message(
                    "❌ This server is not registered for TLT events. Use `/register` first!",
                    ephemeral=True
                )
                return
            
            sub_action = sub_action.lower()
            
            if sub_action == "media":
                await self.handle_media_subcommand(interaction)
            else:
                await interaction.response.send_message(
                    "❌ Invalid promotion sub-action. Use: `media`",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error handling promotion command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the promotion command.",
                ephemeral=True
            )
    
    async def handle_media_subcommand(self, interaction: discord.Interaction):
        """Handle the media sub-command"""
        try:
            # Get available events
            events = self.get_available_events(interaction.guild.id)
            
            if not events:
                await interaction.response.send_message(
                    "❌ No events found! Create an event first using `/tlt create`.",
                    ephemeral=True
                )
                return
            
            # Show the promotion media modal
            from tlt.adapters.discord_adapter.commands.tlt.promotion.modal import PromotionMediaModal
            view = PromotionMediaModal(self.bot_instance, events)
            
            embed = discord.Embed(
                title="📸 Promotion Media Setup",
                description="Upload promotional images for your event to set up the vibe! 🎯",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📋 How it Works",
                value=(
                    "• **Select an Event** - Choose which event to promote\n"
                    "• **Upload Images** - Add promotional images\n"
                    "• **Setup Vibe Check** - Images will be used for photo comparison\n"
                    "• **AI Processing** - Your images help train the photo vibe analysis"
                ),
                inline=False
            )
            embed.add_field(
                name="ℹ️ Note",
                value="These promotional images will be used as reference photos for the event's photo vibe check system.",
                inline=False
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error handling media subcommand: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the media setup.",
                ephemeral=True
            )
    
    async def handle_image_upload(self, interaction: discord.Interaction, event_id: str, image_attachment: discord.Attachment):
        """Handle image upload for promotion setup"""
        try:
            # Validate event exists
            event_message_id = int(event_id)
            if event_message_id not in self.bot_instance.active_events:
                await interaction.response.send_message(
                    "❌ Event not found! It may have been deleted.",
                    ephemeral=True
                )
                return
            
            event_data = self.bot_instance.active_events[event_message_id]
            
            # Validate image attachment
            if not image_attachment.content_type or not image_attachment.content_type.startswith('image/'):
                await interaction.response.send_message(
                    "❌ Please upload a valid image file (JPG, PNG, GIF, etc.).",
                    ephemeral=True
                )
                return
            
            # Download and save the image to the promotion directory
            local_path = await self.bot_instance._download_image(
                attachment=image_attachment,
                guild_id=str(interaction.guild.id),
                user_id=str(interaction.user.id),
                event_id="promotion"  # Special directory for promotion images
            )
            
            if not local_path:
                await interaction.response.send_message(
                    "❌ Failed to save the promotional image. Please try again.",
                    ephemeral=True
                )
                return
            
            # Create CloudEvent for promotion image upload
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.send_promotion_image(
                guild_id=str(interaction.guild.id),
                channel_id=str(interaction.channel.id),
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                event_id=event_id,
                image_url=image_attachment.url,
                local_path=str(local_path),
                event_data=event_data,
                metadata={
                    "source": "discord_promotion_command",
                    "interaction_id": str(interaction.id),
                    "event_topic": event_data.get("topic", "Unknown Event"),
                    "filename": image_attachment.filename,
                    "content_type": image_attachment.content_type,
                    "size": image_attachment.size
                }
            )
            
            if cloudevent_id:
                logger.info(f"Promotion image CloudEvent sent: {cloudevent_id}, event: {event_id}, file: {image_attachment.filename}")
                
                # Send confirmation message
                embed = discord.Embed(
                    title="🎉 Promotion Image Uploaded!",
                    description="Your promotional image has been successfully uploaded and is being processed!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📋 Details",
                    value=(
                        f"**Event:** {event_data.get('topic', 'Unknown')}\n"
                        f"**File:** {image_attachment.filename}\n"
                        f"**Size:** {image_attachment.size:,} bytes\n"
                        f"**CloudEvent ID:** `{cloudevent_id[:8]}...`"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="⏳ Next Steps",
                    value="The AI agent is processing your promotional image and adding it to the event's reference photos for vibe checking!",
                    inline=False
                )
                embed.set_footer(text=f"Uploaded by {interaction.user.display_name}")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            else:
                await interaction.response.send_message(
                    "❌ Failed to process promotional image. Please try again later.",
                    ephemeral=True
                )
                
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid event ID format.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error handling image upload: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing your image upload.",
                ephemeral=True
            )