import discord
from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class EventCreateHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def handle_modal_submission(self, interaction: discord.Interaction, topic: str, location: str, time: str):
        embed = discord.Embed(
            title=f"📅 {topic}",
            description=f"**📍 Location:** {location}\n**🕐 Time:** {time}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Created by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        # Store event
        event_data = {
            "topic": topic,
            "location": location,
            "time": time,
            "creator_id": interaction.user.id,
            "guild_id": interaction.guild.id,
            "channel_id": interaction.channel.id,
            "reactions": {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Check for and clean up existing threads for this message
        await self._cleanup_existing_threads(message)
        
        # Add default reactions with Gen-Z vibes
        default_reactions = ["✅", "❌", "🤔", "🔥", "💯", "👀"]
        for emoji in default_reactions:
            await message.add_reaction(emoji)
            
        # Create public RSVP thread
        try:
            public_thread = await message.create_thread(
                name=f"RSVP: {topic}@{time}",
                auto_archive_duration=10080  # 7 days
            )
            self.bot_instance.event_threads[message.id] = public_thread.id
            
            # Send thread rules for public thread
            rules_embed = discord.Embed(
                title="✨ Vibe Check Zone ✨",
                description="Yo! This thread is emoji-only energy! 🚀\n\n" +
                           "Let's see that vibe 🫣🎉🪩🧠💃🫨",
                color=discord.Color.magenta()
            )
            await public_thread.send(embed=rules_embed)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to create public thread: {e}")
            # Fallback: Use the existing thread if one exists
            try:
                public_thread = await self._find_existing_thread(message, "RSVP:")
                if public_thread:
                    self.bot_instance.event_threads[message.id] = public_thread.id
                    logger.info(f"Using existing public thread: {public_thread.id}")
                else:
                    logger.warning("No public thread found and couldn't create new one")
            except Exception as fallback_error:
                logger.error(f"Fallback thread lookup failed: {fallback_error}")
        
        # Since Discord only allows one thread per message, we'll create the private thread
        # as a separate channel thread instead of a message thread
        try:
            private_thread = await interaction.channel.create_thread(
                name=f"💬 Event Planning: {topic}@{time}",
                auto_archive_duration=10080,  # 7 days
                type=discord.ChannelType.private_thread  # Create as private thread
            )
        except (discord.HTTPException, AttributeError):
            # Fallback: Create as public thread if private threads aren't supported
            try:
                private_thread = await interaction.channel.create_thread(
                    name=f"💬 Event Planning: {topic}",
                    auto_archive_duration=10080  # 7 days
                )
            except discord.HTTPException as e:
                logger.error(f"Failed to create private thread: {e}")
                private_thread = None
        
        # Store private thread reference
        if private_thread:
            event_data["private_thread_id"] = private_thread.id
        self.bot_instance.active_events[message.id] = event_data
        
        # Send welcome message to private thread
        if private_thread:
            private_embed = discord.Embed(
                title="🔒 Private Event Planning",
                description=f"Hey {interaction.user.display_name}! This is your **exclusive** planning space with me for **{topic}**.",
                color=discord.Color.green()
            )
            private_embed.add_field(
                name="⚠️ IMPORTANT - Event Creator Only",
                value=f"🚫 **This thread is restricted to {interaction.user.display_name} only!**\n" +
                      "Other users will be blocked from using commands here.",
                inline=False
            )
            private_embed.add_field(
                name="💡 What's this for?",
                value="\n".join([
                    "• **Event Updates**: Make changes or updates to your event",
                    "• **Photo Management**: Upload promotional images",
                    "• **Analytics**: Get insights on RSVPs and engagement", 
                    "• **Direct Support**: Ask questions about event features",
                    "• **Vibe Coordination**: Manage photo submissions and canvas"
                ]),
                inline=False
            )
            private_embed.add_field(
                name="🚀 Quick Commands",
                value="\n".join([
                    "• Upload images with `!promotion-upload event:{message_id}`",
                    "• Type `help` for available commands",
                    "• Use `/tlt` commands for full features"
                ]).format(message_id=message.id),
                inline=False
            )
            private_embed.set_footer(text="🔒 Creator-only thread | Bot access restricted")
            
            await private_thread.send(f"{interaction.user.mention}", embed=private_embed)
            
            # Add a clear separator message to make privacy obvious
            separator_embed = discord.Embed(
                title="",
                description="═══════════════════════════════════════",
                color=discord.Color.dark_grey()
            )
            await private_thread.send(embed=separator_embed)
        
        # Schedule automatic reminders
        await self.schedule_event_reminders(message.id, time)
        
        # Send event creation to TLT service for ambient agent processing
        try:
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            # Prepare interaction data
            interaction_data = {
                "user_id": str(interaction.user.id),
                "user_name": interaction.user.display_name,
                "guild_id": str(interaction.guild.id),
                "guild_name": interaction.guild.name,
                "channel_id": str(interaction.channel.id),
                "channel_name": interaction.channel.name,
                "command": "create_event",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Interaction data: {interaction_data}")
            
            # Add message ID and thread IDs to event data
            event_data_with_id = event_data.copy()
            event_data_with_id["message_id"] = message.id
            event_data_with_id["public_thread_id"] = public_thread.id
            event_data_with_id["private_thread_id"] = private_thread.id
            logger.info(f"Event data with ID: {event_data_with_id}")

            # Send to TLT service
            task_id = await tlt_client.create_event(
                event_data=event_data_with_id,
                interaction_data=interaction_data,
                message_id=str(message.id),
                priority="normal",
                metadata={"source": "discord_create_command"}
            )
            
            if task_id:
                logger.info(f"Event creation sent to TLT service, task_id: {task_id}")
            else:
                logger.warning("Failed to send event creation to TLT service")
            
            # Save event data to guild_data via TLT service CloudEvent
            try:
                # Send CloudEvent to TLT service to save event data
                save_task_id = await tlt_client.save_event_to_guild_data(
                    event_id=str(message.id),
                    guild_id=str(interaction.guild.id),
                    event_data=event_data_with_id,
                    user_id=str(interaction.user.id),
                    user_name=interaction.user.display_name,
                    metadata={"source": "discord_create_event"},
                    priority="normal"
                )
                
                if save_task_id:
                    logger.info(f"Save event to guild_data CloudEvent sent: {save_task_id}")
                else:
                    logger.warning("Failed to send save event to guild_data CloudEvent")
                    
            except Exception as save_error:
                logger.error(f"Error sending save event CloudEvent: {save_error}")
                # Don't fail the command if save fails
                
        except Exception as e:
            logger.error(f"Error sending event creation to TLT service: {e}")
            # Don't fail the command if TLT service is unavailable
    
    async def schedule_event_reminders(self, message_id: int, event_time_str: str):
        reminder_times = [24, 2, 0.5]  # hours before event
        
        for hours_before in reminder_times:
            # Create simple reminder
            reminder_id = f"{message_id}_auto_{hours_before}h"
            reminder_time = datetime.now(timezone.utc) + timedelta(minutes=1)  # For demo, send in 1 minute
            
            self.bot_instance.active_reminders[reminder_id] = {
                "message_id": message_id,
                "reminder_time": reminder_time.isoformat(),
                "message": f"Event in {hours_before} hours!",
                "status": "pending"
            }
    
    async def _cleanup_existing_threads(self, message: discord.Message):
        """Clean up any existing threads for this message"""
        try:
            # Check if this message already has threads
            if hasattr(message, 'thread') and message.thread:
                logger.info(f"Found existing thread {message.thread.id} for message {message.id}, attempting cleanup")
                try:
                    await message.thread.delete()
                    logger.info(f"Successfully deleted existing thread {message.thread.id}")
                except discord.HTTPException as e:
                    logger.warning(f"Could not delete existing thread: {e}")
            
            # Also check bot's internal tracking
            if message.id in self.bot_instance.event_threads:
                old_thread_id = self.bot_instance.event_threads[message.id]
                try:
                    # Try to get and delete the thread
                    old_thread = message.guild.get_thread(old_thread_id)
                    if old_thread:
                        await old_thread.delete()
                        logger.info(f"Deleted tracked thread {old_thread_id}")
                except Exception as e:
                    logger.warning(f"Could not delete tracked thread {old_thread_id}: {e}")
                
                # Remove from tracking
                del self.bot_instance.event_threads[message.id]
            
            # Check for existing events and clean up their thread references
            if message.id in self.bot_instance.active_events:
                old_event = self.bot_instance.active_events[message.id]
                
                # Clean up public thread
                if "public_thread_id" in old_event:
                    try:
                        old_public_thread = message.guild.get_thread(old_event["public_thread_id"])
                        if old_public_thread:
                            await old_public_thread.delete()
                            logger.info(f"Deleted old public thread {old_event['public_thread_id']}")
                    except Exception as e:
                        logger.warning(f"Could not delete old public thread: {e}")
                
                # Clean up private thread
                if "private_thread_id" in old_event:
                    try:
                        old_private_thread = message.guild.get_thread(old_event["private_thread_id"])
                        if old_private_thread:
                            await old_private_thread.delete()
                            logger.info(f"Deleted old private thread {old_event['private_thread_id']}")
                    except Exception as e:
                        logger.warning(f"Could not delete old private thread: {e}")
                        
        except Exception as e:
            logger.error(f"Error during thread cleanup: {e}")
    
    async def _find_existing_thread(self, message: discord.Message, name_prefix: str):
        """Find an existing thread with the given name prefix"""
        try:
            # Check all threads in the guild
            for thread in message.guild.threads:
                if thread.name.startswith(name_prefix) and thread.parent_id == message.channel.id:
                    return thread
            return None
        except Exception as e:
            logger.error(f"Error finding existing thread: {e}")
            return None