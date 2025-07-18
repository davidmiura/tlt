import discord
from typing import TYPE_CHECKING, List, Tuple
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class VibeHandler:
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
    
    async def handle_vibe_command(self, interaction: discord.Interaction):
        """Handle the /tlt vibe command"""
        try:
            # Check if guild is registered
            if not self.bot_instance.is_guild_registered(interaction.guild.id):
                await interaction.response.send_message(
                    "❌ This server is not registered for TLT events. Use `/register` first!",
                    ephemeral=True
                )
                return
            
            # Get available events
            events = self.get_available_events(interaction.guild.id)
            
            if not events:
                await interaction.response.send_message(
                    "❌ No events found! Create an event first using `/tlt create`.",
                    ephemeral=True
                )
                return
            
            # Show the vibe modal
            from tlt.adapters.discord_adapter.commands.tlt.vibe.modal import VibeModal
            view = VibeModal(self.bot_instance, events)
            
            embed = discord.Embed(
                title="✨ Vibe Actions",
                description="Choose an event and pick what you want to do with the vibe! 🎯",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="📸 Available Actions",
                value=(
                    "• **Generate Event Slideshow** - Create photo slideshow\n"
                    "• **Create Vibe Snapshot** - Get event analysis\n" 
                    "• **Get Vibe Canvas Preview** - View collaborative canvas\n"
                    "• **Get Event Photo Summary** - Photo stats"
                ),
                inline=False
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error handling vibe command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the vibe command.",
                ephemeral=True
            )
    
    async def handle_vibe_submission(self, interaction: discord.Interaction, event_id: str, action: str):
        """Handle vibe action submission"""
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
            
            # Create CloudEvent for vibe action
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.send_vibe_action(
                guild_id=str(interaction.guild.id),
                channel_id=str(interaction.channel.id),
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                event_id=event_id,
                action=action,
                event_data=event_data,
                metadata={
                    "source": "discord_vibe_command",
                    "interaction_id": str(interaction.id),
                    "event_topic": event_data.get("topic", "Unknown Event"),
                    "action_type": action
                }
            )
            
            if cloudevent_id:
                logger.info(f"Vibe action CloudEvent sent: {cloudevent_id}, action: {action}, event: {event_id}")
                
                # Send confirmation message
                action_names = {
                    "generate_event_slideshow": "📸 Event Slideshow Generation",
                    "create_vibe_snapshot": "📊 Vibe Snapshot Creation", 
                    "get_vibe_canvas_preview": "🎨 Vibe Canvas Preview",
                    "get_event_photo_summary": "📷 Event Photo Summary"
                }
                
                action_name = action_names.get(action, action)
                
                embed = discord.Embed(
                    title="🚀 Vibe Action Submitted!",
                    description=f"Your **{action_name}** request has been submitted and is being processed!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📋 Details",
                    value=(
                        f"**Event:** {event_data.get('topic', 'Unknown')}\n"
                        f"**Action:** {action_name}\n"
                        f"**CloudEvent ID:** `{cloudevent_id[:8]}...`"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="⏳ Next Steps",
                    value="The AI agent is processing your request. Results will be delivered shortly!",
                    inline=False
                )
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            else:
                await interaction.response.send_message(
                    "❌ Failed to submit vibe action. Please try again later.",
                    ephemeral=True
                )
                
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid event ID format.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error handling vibe submission: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing your vibe action.",
                ephemeral=True
            )