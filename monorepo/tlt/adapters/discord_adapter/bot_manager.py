import discord
from discord.ext import commands
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone
import asyncio
import aiohttp
import aiofiles
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Import all managers and handlers
from tlt.adapters.discord_adapter.guild_management.manager import GuildManager
from tlt.adapters.discord_adapter.permissions.checker import PermissionChecker
from tlt.adapters.discord_adapter.reaction_handlers.manager import ReactionManager
from tlt.adapters.discord_adapter.message_moderation.enforcer import MessageModerationEnforcer
from tlt.adapters.discord_adapter.event_artifacts.generator import EventArtifactGenerator
from tlt.adapters.discord_adapter.slash_commands.setup import SlashCommandSetup
from tlt.adapters.discord_adapter.event_bridge.handlers import EventBridgeHandlers
from tlt.adapters.discord_adapter.reminder_bridge.handlers import ReminderBridgeHandlers
from tlt.adapters.discord_adapter.tasks.reminder_check.task import ReminderCheckTask
from tlt.adapters.discord_adapter.tasks.reminder_check.handler import ReminderHandler

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        intents.guilds = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        # Bot state
        self.guild_settings: Dict[int, Dict] = {}
        self.registered_guilds: Dict[int, Dict] = {}
        self.active_events: Dict[int, Dict] = {}
        self.active_reminders: Dict[str, Dict] = {}
        self.experiences: Dict[str, Dict] = {}
        self.event_threads: Dict[int, int] = {}  # message_id -> thread_id
        
        # Initialize all managers and handlers
        self.guild_manager = GuildManager(self)
        self.permission_checker = PermissionChecker(self)
        self.reaction_manager = ReactionManager(self)
        self.message_enforcer = MessageModerationEnforcer(self)
        self.artifact_generator = EventArtifactGenerator(self)
        self.slash_command_setup = SlashCommandSetup(self)
        self.event_bridge = EventBridgeHandlers(self)
        self.reminder_bridge = ReminderBridgeHandlers(self)
        self.reminder_check_task = ReminderCheckTask(self)
        self.reminder_handler = ReminderHandler(self)
        
        # State querying for ambient agent integration
        self.state_query_task = None
        
    async def setup_hook(self):
        """Initialize bot settings and load extensions"""
        logger.info("Setting up bot...")
        self.reminder_check_task.start()
        await self.slash_command_setup.setup_slash_commands()
        
        # Start state query task
        self.state_query_task = asyncio.create_task(self._state_query_loop())
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    # Event handlers - delegate to appropriate managers
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild"""
        await self.guild_manager.on_guild_join(guild)
        
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild"""
        await self.guild_manager.on_guild_remove(guild)
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction additions"""
        await self.reaction_manager.on_reaction_add(reaction, user)
    
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction removals"""
        await self.reaction_manager.on_reaction_remove(reaction, user)
    
    async def on_message(self, message: discord.Message):
        """Handle messages in event threads and DMs"""
        # Skip bot messages
        if message.author.bot:
            return
            
        # Handle DMs with photo vibe check
        if isinstance(message.channel, discord.DMChannel):
            await self._handle_dm_message(message)
        else:
            # Check for promotion image uploads first
            if "!promotion-upload" in message.content.lower() and message.attachments:
                await self._handle_promotion_image_upload(message)
                return  # Promotion image processed, skip other handling
            
            # Check if this is a private event planning thread
            if hasattr(message.channel, 'parent') and message.channel.parent:
                # Check if this is a private thread (by name pattern)
                if message.channel.name.startswith("💬 Event Planning:"):
                    await self._handle_private_thread_message(message)
                    return  # Private thread handled, skip other processing
                
                # This is a thread message - check for photos in public threads
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type and attachment.content_type.startswith('image/'):
                            await self._handle_thread_photo_submission(message, attachment)
                            return  # Photo processed, skip message enforcement
            
            # Handle other guild messages (emoji enforcement, etc.)
            await self.message_enforcer.on_message(message)
    
    # Delegation methods for backward compatibility
    def get_guild_settings(self, guild_id: int) -> Optional[Dict]:
        """Get settings for a specific guild"""
        return self.guild_manager.get_guild_settings(guild_id)
        
    def update_guild_settings(self, guild_id: int, settings: Dict):
        """Update settings for a specific guild"""
        return self.guild_manager.update_guild_settings(guild_id, settings)
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if member is admin"""
        return self.permission_checker.is_admin(member)
    
    def is_guild_registered(self, guild_id: int) -> bool:
        """Check if guild is registered"""
        return self.guild_manager.is_guild_registered(guild_id)
    
    async def register_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Register a guild for TLT events"""
        return await self.guild_manager.register_guild(guild, admin)
    
    async def deregister_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Deregister a guild from TLT events"""
        return await self.guild_manager.deregister_guild(guild, admin)
    
    async def create_event_from_modal(self, interaction: discord.Interaction, topic: str, location: str, time: str):
        """Create a new event from modal submission"""
        await self.event_bridge.create_event_from_modal(interaction, topic, location, time)
    
    async def update_event_from_modal(self, interaction: discord.Interaction, message_id: int, topic: str, location: str, time: str):
        """Update an existing event from modal submission"""
        await self.event_bridge.update_event_from_modal(interaction, message_id, topic, location, time)
    
    async def send_reminder(self, reminder_id: str):
        """Delegate to reminder handler"""
        await self.reminder_bridge.send_reminder(reminder_id)
    
    async def schedule_event_reminders(self, message_id: int, event_time_str: str):
        """Delegate to reminder handler"""
        await self.reminder_bridge.schedule_event_reminders(message_id, event_time_str)
    
    async def generate_event_artifact(self, message_id: int):
        """Generate post-event artifact"""
        await self.artifact_generator.generate_event_artifact(message_id)
    
    async def _state_query_loop(self):
        """Periodically query TLT service for agent state updates"""
        import os
        import httpx
        
        tlt_service_url = os.getenv("TLT_SERVICE_URL", "http://localhost:8008")
        query_interval = int(os.getenv("STATE_QUERY_INTERVAL", "30"))  # seconds
        
        logger.info(f"Starting state query loop (interval: {query_interval}s)")
        
        while True:
            try:
                await asyncio.sleep(query_interval)
                
                # Query TLT service for agent state updates
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{tlt_service_url}/monitor/agent/state")
                    
                    if response.status_code == 200:
                        agent_state = response.json()
                        await self._process_agent_state_updates(agent_state)
                    else:
                        logger.warning(f"Failed to query agent state: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Error in state query loop: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _process_agent_state_updates(self, agent_state: dict):
        """Process agent state updates and take appropriate Discord actions"""
        try:
            # Check for guild-specific state updates
            guild_states = agent_state.get("agent_state_by_guild", {})
            
            for guild_id_str, guild_state in guild_states.items():
                guild_id = int(guild_id_str)
                guild = self.get_guild(guild_id)
                
                if not guild:
                    continue
                
                # Check for pending messages to send
                pending_messages = guild_state.get("pending_messages", [])
                for message_info in pending_messages:
                    await self._send_agent_message(guild, message_info)
                
                # Check for event updates
                event_updates = guild_state.get("event_updates", [])
                for event_update in event_updates:
                    await self._process_event_update(guild, event_update)
                
                # Check for user-specific notifications
                user_notifications = guild_state.get("user_notifications", [])
                for notification in user_notifications:
                    await self._send_user_notification(guild, notification)
                    
        except Exception as e:
            logger.error(f"Error processing agent state updates: {e}")
    
    async def _send_agent_message(self, guild: discord.Guild, message_info: dict):
        """Send a message from the agent to Discord"""
        try:
            channel_id = message_info.get("channel_id")
            content = message_info.get("content")
            
            if not channel_id or not content:
                return
            
            channel = guild.get_channel(int(channel_id))
            if channel:
                await channel.send(content)
                logger.info(f"Sent agent message to {guild.name}#{channel.name}")
                
        except Exception as e:
            logger.error(f"Error sending agent message: {e}")
    
    async def _process_event_update(self, guild: discord.Guild, event_update: dict):
        """Process an event update from the agent"""
        try:
            event_id = event_update.get("event_id")
            update_type = event_update.get("update_type")
            
            if event_id in self.active_events:
                event = self.active_events[event_id]
                
                if update_type == "rsvp_summary":
                    # Update event embed with new RSVP data
                    await self._update_event_embed_with_rsvp_data(guild, event, event_update)
                elif update_type == "reminder_sent":
                    # Log reminder sent
                    logger.info(f"Reminder sent for event {event_id}")
                    
        except Exception as e:
            logger.error(f"Error processing event update: {e}")
    
    async def _update_event_embed_with_rsvp_data(self, guild: discord.Guild, event: dict, rsvp_data: dict):
        """Update event embed with RSVP insights from agent"""
        try:
            # Get the event message
            channel = guild.get_channel(event.get("channel_id"))
            if not channel:
                return
            
            message = await channel.fetch_message(event.get("message_id"))
            if not message:
                return
            
            # Get current embed
            embed = message.embeds[0] if message.embeds else None
            if not embed:
                return
            
            # Add agent insights
            attendance_predictions = rsvp_data.get("attendance_predictions", {})
            if attendance_predictions:
                high_confidence_attendees = [
                    user_id for user_id, prediction in attendance_predictions.items()
                    if prediction.get("attendance_score", 0) > 0.8
                ]
                
                if high_confidence_attendees:
                    embed.add_field(
                        name="🤖 Agent Insights",
                        value=f"High confidence attendees: {len(high_confidence_attendees)}",
                        inline=False
                    )
                    
                    await message.edit(embed=embed)
                    logger.info(f"Updated event embed with agent insights for {event.get('topic', 'Unknown')}")
                    
        except Exception as e:
            logger.error(f"Error updating event embed with RSVP data: {e}")
    
    async def _send_user_notification(self, guild: discord.Guild, notification: dict):
        """Send a private notification to a user"""
        try:
            user_id = notification.get("user_id")
            message = notification.get("message")
            
            if not user_id or not message:
                return
            
            user = guild.get_member(int(user_id))
            if user:
                await user.send(message)
                logger.info(f"Sent private notification to {user.display_name}")
                
        except Exception as e:
            logger.error(f"Error sending user notification: {e}")
    
    async def _download_image(self, attachment: discord.Attachment, guild_id: str, user_id: str, event_id: Optional[str] = None, category: Optional[str] = None) -> Optional[str]:
        """Download image and store locally by guild/user/event structure.
        
        Args:
            attachment: Discord attachment object
            guild_id: Guild ID or 'dm_channel' for DMs
            user_id: User ID who submitted the photo
            event_id: Event ID if available
            
        Returns:
            Local file path if successful, None if failed
        """
        try:
            # Create directory structure using GUILD_DATA_DIR: 
            # - All images: guild_data/data/{guild_id}/{event_id or 'general'}/{user_id}/{category}
            # - Promotion images: guild_data/data/{guild_id}/{event_id}/{user_id}/promotion
            data_dir = Path(os.getenv('GUILD_DATA_DIR', './guild_data'))
            base_dir = data_dir / "data"
            event_folder = event_id if event_id else "general"
            
            # Always include user_id in path to track who uploaded images
            if category:
                image_dir = base_dir / guild_id / event_folder / user_id / category
            else:
                image_dir = base_dir / guild_id / event_folder / user_id
            
            # Create directories if they don't exist
            image_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(attachment.filename).suffix or ".jpg"
            local_filename = f"{timestamp}_{attachment.filename}"
            local_filepath = image_dir / local_filename
            
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        async with aiofiles.open(local_filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        logger.info(f"Downloaded image: {local_filepath}")
                        return str(local_filepath)
                    else:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None

    async def _handle_thread_photo_submission(self, message: discord.Message, attachment: discord.Attachment):
        """Handle photo submission in event threads"""
        try:
            # Find the event associated with this thread
            event_id = None
            event_message_id = None
            
            for msg_id, thread_id in self.event_threads.items():
                if thread_id == message.channel.id:
                    event_message_id = msg_id
                    break
            
            if event_message_id and event_message_id in self.active_events:
                event = self.active_events[event_message_id]
                # Use the event's unique identifier as event_id
                event_id = str(event_message_id)  # Use message ID as event identifier
            
            if not event_id:
                logger.warning(f"Could not find event for thread {message.channel.id}")
                await message.reply("❌ Could not associate this photo with an event.")
                return
            
            # Download the image and store locally
            local_image_path = await self._download_image(
                attachment=attachment,
                guild_id=str(message.guild.id),
                user_id=str(message.author.id),
                event_id=event_id
            )
            
            if not local_image_path:
                await message.reply("❌ Failed to download your photo. Please try again later.")
                return
            
            # Send CloudEvent to TLT service for photo processing
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.send_photo_vibe_check(
                guild_id=str(message.guild.id),
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                user_name=message.author.display_name,
                photo_url=attachment.url,
                filename=attachment.filename,
                event_id=event_id,
                content_type=attachment.content_type,
                size=attachment.size,
                message_content=message.content,
                metadata={
                    "source": "discord_thread_photo_submission",
                    "message_id": str(message.id),
                    "thread_id": str(message.channel.id),
                    "parent_channel_id": str(message.channel.parent.id),
                    "event_message_id": str(event_message_id),
                    "timestamp": message.created_at.isoformat(),
                    "local_image_path": local_image_path,
                    "original_filename": attachment.filename,
                    "downloaded_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            if cloudevent_id:
                logger.info(f"Thread photo vibe check CloudEvent sent: {cloudevent_id}, local path: {local_image_path}")
                
                # Send confirmation to user with emoji reaction
                await message.add_reaction("📸")
                await message.reply(
                    f"📸 Thanks for your photo! I'm processing it for vibe check analysis for this event. "
                    "You'll receive feedback about how it matches the event vibe!"
                )
            else:
                await message.reply("❌ Sorry, I couldn't process your photo submission right now. Please try again later.")
                
        except Exception as e:
            logger.error(f"Error processing thread photo submission: {e}")
            await message.reply("❌ There was an error processing your photo. Please try again later.")

    async def _handle_dm_message(self, message: discord.Message):
        """Handle DM messages, especially photo submissions for vibe check"""
        try:
            # Skip bot messages
            if message.author.bot:
                return
            
            # Check if message contains attachments (photos)
            if message.attachments:
                for attachment in message.attachments:
                    # Check if attachment is an image
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        await self._process_photo_submission(message, attachment)
                        return
            
            # Check for text-based photo submissions (URLs)
            if any(url_indicator in message.content.lower() for url_indicator in ['http', 'imgur', 'photos', 'image']):
                await self._process_photo_url_submission(message)
                return
            
            # Check for event-related keywords
            if any(keyword in message.content.lower() for keyword in ['event', 'vibe', 'check', 'photo', 'picture']):
                await self._send_photo_vibe_check_instructions(message)
                
        except Exception as e:
            logger.error(f"Error handling DM message: {e}")
    
    async def _process_photo_submission(self, message: discord.Message, attachment: discord.Attachment):
        """Process a photo submission for vibe check"""
        try:
            # Send CloudEvent to TLT service for photo processing
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            # Extract event ID from message content if provided (e.g., "event:123456")
            event_id = None
            guild_id = None
            
            if message.content:
                import re
                event_match = re.search(r'event:(\w+)', message.content.lower())
                if event_match:
                    event_id = event_match.group(1)
                    
                    # Look up guild_id from active_events using event_id (message_id)
                    try:
                        event_message_id = int(event_id)
                        if event_message_id in self.active_events:
                            event_data = self.active_events[event_message_id]
                            guild_id = str(event_data.get("guild_id", ""))
                            logger.info(f"Found guild_id {guild_id} for event {event_id}")
                        else:
                            logger.warning(f"Event {event_id} not found in active_events")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid event_id format: {event_id}, error: {e}")
            
            # Use guild_id if found, otherwise fall back to DM identifier
            effective_guild_id = guild_id if guild_id else "dm_channel"
            
            # Download the image and store locally
            local_image_path = await self._download_image(
                attachment=attachment,
                guild_id=effective_guild_id,
                user_id=str(message.author.id),
                event_id=event_id
            )
            
            if not local_image_path:
                await message.reply(
                    "❌ Failed to download your photo. Please try again later."
                )
                return
            
            # Create CloudEvent for photo submission using dedicated photo vibe check event
            cloudevent_id = await tlt_client.send_photo_vibe_check(
                guild_id=effective_guild_id,
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                user_name=message.author.display_name,
                photo_url=attachment.url,
                filename=attachment.filename,
                event_id=event_id,
                content_type=attachment.content_type,
                size=attachment.size,
                message_content=message.content,
                metadata={
                    "source": "discord_dm_photo_submission",
                    "message_id": str(message.id),
                    "timestamp": message.created_at.isoformat(),
                    "local_image_path": local_image_path,
                    "original_filename": attachment.filename,
                    "downloaded_at": datetime.now(timezone.utc).isoformat(),
                    "guild_id": guild_id  # Pass guild_id in metadata for GenZ vibe check
                }
            )
            
            if cloudevent_id:
                logger.info(f"Photo vibe check CloudEvent sent: {cloudevent_id}, local path: {local_image_path}")
                
                # Send confirmation to user with GenZ vibe
                event_context = f" for event {event_id}" if event_id else ""
                genZ_responses = [
                    f"📸 yooo that pic goes hard{event_context}! 🔥 running the vibe check rn... gonna see if you're matching the energy fr fr 💯",
                    f"📸 okay okay I see you with that photo{event_context}! ✨ putting it through the vibe scanner... this better slap 👀💅",
                    f"📸 periodt that's a LOOK{event_context}! 🫧 checking if you understood the assignment... stand by bestie 🚀",
                    f"📸 no cap that's fire{event_context}! 🔥 running diagnostics on your vibe level... better not be mid 💀✨"
                ]
                
                import random
                response = random.choice(genZ_responses)
                await message.reply(response)
            else:
                await message.reply(
                    "❌ bruh the vibe check machine is broken rn 😭 try again later bestie, this is not it 💀"
                )
                
        except Exception as e:
            logger.error(f"Error processing photo submission: {e}")
            await message.reply(
                "❌ bestie something went wrong with your vibe check 💀 the bot is having a moment... try again later fr 😅"
            )
    
    async def _process_photo_url_submission(self, message: discord.Message):
        """Process a photo URL submission"""
        try:
            # Extract potential URLs from message
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
            
            if not urls:
                return
            
            # Send CloudEvent for URL-based photo submission
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            photo_data = {
                "user_id": str(message.author.id),
                "user_name": message.author.display_name,
                "photo_urls": urls,
                "message_content": message.content,
                "timestamp": message.created_at.isoformat()
            }
            
            cloudevent_id = await tlt_client.send_discord_message(
                guild_id="dm_channel",
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                content=f"Photo URL vibe check submission: {len(urls)} URLs",
                message_id=str(message.id),
                message_type="photo_vibe_check_url",
                priority="normal",
                metadata={
                    "source": "discord_dm_photo_url_submission",
                    "photo_data": photo_data
                }
            )
            
            if cloudevent_id:
                await message.reply(
                    f"📸 Thanks for submitting {len(urls)} photo URL(s)! I'm processing them for vibe check analysis."
                )
            else:
                await message.reply(
                    "❌ Sorry, I couldn't process your photo URLs right now. Please try again later."
                )
                
        except Exception as e:
            logger.error(f"Error processing photo URL submission: {e}")
    
    async def _send_photo_vibe_check_instructions(self, message: discord.Message):
        """Send instructions for photo vibe check"""
        try:
            instructions = """
📸 **Photo Vibe Check Instructions**

To submit photos for event vibe checking:

1. **Upload directly**: Attach image files to your DM
2. **Share URLs**: Send links to photos (Imgur, Google Photos, etc.)
3. **Include event ID**: Add `event:EVENT_ID` in your message (e.g., "event:123456")
4. **Include context**: Add a message about the event or photo

**What I analyze:**
• How well your photo matches the event's vibe
• Attendance confirmation through photo analysis
• Overall event atmosphere and engagement

**Supported formats**: JPG, PNG, GIF, WebP
**Storage**: Images are stored locally organized by guild/user/event

**Example**: Send a photo with message "Here's my pic from the party! event:123456"

Just send your photos and I'll take care of the rest! 🎉
            """
            
            await message.reply(instructions)
            
        except Exception as e:
            logger.error(f"Error sending photo vibe check instructions: {e}")

    async def _handle_private_thread_message(self, message: discord.Message):
        """Handle messages in private event planning threads"""
        try:
            # Find the associated event for this private thread
            event_data = None
            event_message_id = None
            
            for message_id, event_info in self.active_events.items():
                if event_info.get("private_thread_id") == message.channel.id:
                    event_data = event_info
                    event_message_id = message_id
                    break
            
            if not event_data:
                await message.reply("❌ Unable to find the associated event for this planning thread.")
                return
            
            # Check if user is the event creator
            if message.author.id != event_data.get("creator_id"):
                await message.reply("❌ Only the event creator can use this private planning thread.")
                return
            
            content = message.content.lower()
            
            # Handle help command
            if content in ["help", "commands", "?", "what can you do"]:
                await self._send_private_thread_help(message, event_message_id, event_data)
                return
            
            # Handle promotion image uploads in private thread
            if "!promotion-upload" in content and message.attachments:
                await self._handle_promotion_image_upload(message)
                return
            
            # Handle event info request
            if any(keyword in content for keyword in ["info", "details", "status", "analytics"]):
                await self._send_event_analytics(message, event_message_id, event_data)
                return
            
            # Handle general photo uploads (for promotion)
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        await self._handle_private_photo_upload(message, attachment, event_message_id, event_data)
                        return
            
            # Default response for unrecognized commands
            await message.reply(
                f"👋 Hey! I didn't recognize that command. Type `help` to see what I can do in this private planning space.\n\n"
                f"💡 **Quick tip**: You can upload promotional images directly here or use `!promotion-upload event:{event_message_id}`"
            )
            
        except Exception as e:
            logger.error(f"Error handling private thread message: {e}")
            await message.reply("❌ Sorry, I encountered an error processing your message.")

    async def _send_private_thread_help(self, message: discord.Message, event_message_id: int, event_data: dict):
        """Send help information for private thread commands"""
        try:
            event_topic = event_data.get("topic", "Unknown Event")
            
            help_embed = discord.Embed(
                title="🤖 Private Planning Commands",
                description=f"Here's what I can help you with for **{event_topic}**:",
                color=discord.Color.blue()
            )
            
            help_embed.add_field(
                name="📸 Photo Management",
                value="\n".join([
                    f"• Upload images directly (I'll automatically add them as promotional photos)",
                    f"• `!promotion-upload event:{event_message_id}` - Structured upload command",
                    "• Images are stored for vibe checking reference"
                ]),
                inline=False
            )
            
            help_embed.add_field(
                name="📊 Event Analytics",
                value="\n".join([
                    "• `info` or `status` - Get current event metrics",
                    "• `analytics` - Detailed RSVP and engagement data",
                    "• View attendance predictions and insights"
                ]),
                inline=False
            )
            
            help_embed.add_field(
                name="🔧 General Commands",
                value="\n".join([
                    "• `help` - Show this help message",
                    "• Upload any image to add as promotional reference",
                    "• Use `/tlt` slash commands for full features"
                ]),
                inline=False
            )
            
            help_embed.set_footer(text=f"Event ID: {event_message_id} | Private thread between you and TLT bot")
            
            await message.reply(embed=help_embed)
            
        except Exception as e:
            logger.error(f"Error sending private thread help: {e}")

    async def _send_event_analytics(self, message: discord.Message, event_message_id: int, event_data: dict):
        """Send event analytics and status information"""
        try:
            # Get RSVP data from reactions
            rsvp_summary = event_data.get("reactions", {})
            total_rsvps = sum(len(users) for users in rsvp_summary.values())
            
            analytics_embed = discord.Embed(
                title="📊 Event Analytics",
                description=f"**{event_data.get('topic', 'Unknown Event')}**",
                color=discord.Color.green()
            )
            
            analytics_embed.add_field(
                name="📅 Event Details",
                value="\n".join([
                    f"**Location:** {event_data.get('location', 'Not specified')}",
                    f"**Time:** {event_data.get('time', 'Not specified')}",
                    f"**Created:** {event_data.get('created_at', 'Unknown')[:10]}",  # Just date
                    f"**Message ID:** {event_message_id}"
                ]),
                inline=False
            )
            
            analytics_embed.add_field(
                name="👥 RSVP Summary",
                value=f"**Total Responses:** {total_rsvps}" + (
                    "\n" + "\n".join([f"**{emoji}:** {len(users)}" for emoji, users in rsvp_summary.items()])
                    if rsvp_summary else "\nNo RSVPs yet"
                ),
                inline=False
            )
            
            analytics_embed.add_field(
                name="🔗 Thread Links",
                value="\n".join([
                    f"**Public RSVP Thread:** <#{event_data.get('public_thread_id', 'Unknown')}>",
                    f"**Private Planning:** This thread",
                    f"**Main Event Post:** [Jump to message](https://discord.com/channels/{event_data.get('guild_id')}/{event_data.get('channel_id')}/{event_message_id})"
                ]),
                inline=False
            )
            
            analytics_embed.set_footer(text="💡 Use /tlt commands for more advanced features")
            
            await message.reply(embed=analytics_embed)
            
        except Exception as e:
            logger.error(f"Error sending event analytics: {e}")

    async def _handle_private_photo_upload(self, message: discord.Message, attachment: discord.Attachment, event_message_id: int, event_data: dict):
        """Handle photo uploads in private threads (automatically treat as promotional)"""
        try:
            # Download the image to the promotion directory
            local_path = await self._download_image(
                attachment=attachment,
                guild_id=str(message.guild.id),
                user_id=str(message.author.id),
                event_id=str(event_message_id),
                category="promotion"
            )
            
            if not local_path:
                await message.reply("❌ Failed to save the promotional image. Please try again.")
                return
            
            # Create CloudEvent for promotion image upload
            from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
            
            cloudevent_id = await tlt_client.send_promotion_image(
                guild_id=str(message.guild.id),
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                user_name=message.author.display_name,
                event_id=str(event_message_id),
                image_url=attachment.url,
                local_path=str(local_path),
                event_data=event_data,
                metadata={
                    "source": "discord_private_thread_upload",
                    "message_id": str(message.id),
                    "event_topic": event_data.get("topic", "Unknown Event"),
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "size": attachment.size,
                    "upload_method": "private_thread"
                }
            )
            
            if cloudevent_id:
                logger.info(f"Private thread promotion image CloudEvent sent: {cloudevent_id}, event: {event_message_id}")
                
                # Cross-post the promotional image to the RSVP thread with Gen-Z vibe
                await self._cross_post_to_rsvp_thread(message, attachment, event_data, event_message_id)
                
                # Send confirmation
                await message.add_reaction("📸")
                await message.reply(
                    f"🎉 **Promotional Image Added!**\n\n"
                    f"📁 **File:** {attachment.filename}\n"
                    f"💾 **Size:** {attachment.size:,} bytes\n"
                    f"🆔 **CloudEvent ID:** `{cloudevent_id[:8]}...`\n\n"
                    f"✅ This image has been added as a promotional reference for **{event_data.get('topic', 'your event')}** and will be used for photo vibe checking!\n\n"
                    f"🔥 **Plus:** I've shared this fire content in the RSVP thread to get everyone hyped! 📸✨"
                )
            else:
                await message.reply("❌ Failed to process promotional image. Please try again later.")
                
        except Exception as e:
            logger.error(f"Error handling private photo upload: {e}")
            await message.reply("❌ There was an error processing your photo upload.")

    async def _cross_post_to_rsvp_thread(self, message: discord.Message, attachment: discord.Attachment, event_data: dict, event_message_id: int):
        """Cross-post promotional image to RSVP thread with Gen-Z vibe"""
        try:
            logger.info(f"Starting cross-post to RSVP thread for event {event_message_id}")
            
            # Get the public RSVP thread
            public_thread_id = event_data.get("public_thread_id")
            logger.info(f"Event data public_thread_id: {public_thread_id}")
            
            if not public_thread_id:
                # Fallback: try to find it in event_threads
                public_thread_id = self.event_threads.get(event_message_id)
                logger.info(f"Fallback event_threads lookup: {public_thread_id}")
            
            if not public_thread_id:
                logger.warning(f"No public thread found for event {event_message_id}. Event data keys: {list(event_data.keys())}")
                logger.warning(f"Available event_threads: {list(self.event_threads.keys())}")
                return
            
            # Get the thread object
            public_thread = message.guild.get_thread(public_thread_id)
            logger.info(f"Thread lookup result: {public_thread}")
            
            if not public_thread:
                logger.warning(f"Public thread {public_thread_id} not found or archived")
                # Try to fetch from API if not in cache
                try:
                    public_thread = await message.guild.fetch_channel(public_thread_id)
                    logger.info(f"Fetched thread from API: {public_thread}")
                except Exception as fetch_error:
                    logger.error(f"Failed to fetch thread {public_thread_id} from API: {fetch_error}")
                    return
            
            if not public_thread:
                logger.error(f"Unable to find public thread {public_thread_id} after all attempts")
                return
            
            # Create Gen-Z vibe messages (randomize for variety)
            import random
            gen_z_messages = [
                f"🔥 **{message.author.display_name} just dropped the PROMO** 🔥\n\nThis is giving main character energy fr fr 💅✨",
                f"📸 **NEW PROMO ALERT** 📸\n\n{message.author.display_name} said \"let me set the vibe\" and honestly? We're here for it 🎯💯",
                f"✨ **PROMOTION MOMENT** ✨\n\nY'all... {message.author.display_name} really understood the assignment 🫶 This is it, this is the one!",
                f"🎉 **VIBE CHECK: PASSED** 🎉\n\n{message.author.display_name} really said \"watch me promote this event\" and we're obsessed 🤩💖",
                f"💫 **EVENT PROMO JUST LANDED** 💫\n\nNot {message.author.display_name} serving LOOKS for this event 😍 We love to see it bestie!",
                f"🌟 **PROMOTIONAL EXCELLENCE** 🌟\n\n{message.author.display_name} really captured the whole entire vibe with this one ✨ No notes!",
                f"📺 **MAIN CHARACTER MOMENT** 📺\n\nEveryone gather round - {message.author.display_name} just posted THE promo and it's giving everything! 🔥💯"
            ]
            
            # Random selection for variety
            promo_message = random.choice(gen_z_messages)
            
            # Create the cross-post embed
            cross_post_embed = discord.Embed(
                title="📸 Event Promo Drop!",
                description=promo_message,
                color=discord.Color.from_rgb(255, 105, 180)  # Hot pink for that Gen-Z energy
            )
            cross_post_embed.add_field(
                name="🎯 Event Deets",
                value=f"**{event_data.get('topic', 'This Event')}**\n📍 {event_data.get('location', 'TBA')}\n⏰ {event_data.get('time', 'TBA')}",
                inline=False
            )
            cross_post_embed.add_field(
                name="💡 Pro Tip",
                value="React with your vibe below! This promo is setting the tone for what's about to be an ICONIC event ✨",
                inline=False
            )
            cross_post_embed.set_image(url=attachment.url)
            cross_post_embed.set_footer(
                text=f"Promo by {message.author.display_name} | React to show your excitement! 🎉",
                icon_url=message.author.display_avatar.url
            )
            
            # Post to RSVP thread
            cross_post_message = await public_thread.send(embed=cross_post_embed)
            
            # Add Gen-Z reactions for engagement
            gen_z_reactions = ["🔥", "💯", "✨", "🤩", "👑", "💖", "🎯", "📸"]
            for emoji in random.sample(gen_z_reactions, 4):  # Random 4 reactions
                try:
                    await cross_post_message.add_reaction(emoji)
                except discord.HTTPException:
                    continue  # Skip if reaction fails
            
            logger.info(f"Successfully cross-posted promotion image to RSVP thread {public_thread_id}")
            
        except Exception as e:
            logger.error(f"Error cross-posting to RSVP thread: {e}")
            # Don't fail the main upload process if cross-posting fails

    async def _handle_promotion_image_upload(self, message: discord.Message):
        """Handle promotion image uploads via message content with !promotion-upload"""
        try:
            # Check if user has pending promotion upload
            user_id = str(message.author.id)
            guild_id = str(message.guild.id)
            
            # Look for pending promotion uploads (this would be set by the modal)
            # For now, we'll process any image with !promotion-upload
            
            # Validate message has image attachments
            if not message.attachments:
                await message.reply("❌ Please upload an image file with your promotion message.")
                return
            
            # Process each image attachment
            for attachment in message.attachments:
                if not attachment.content_type or not attachment.content_type.startswith('image/'):
                    await message.reply("❌ Please upload a valid image file (JPG, PNG, GIF, etc.).")
                    continue
                
                # Extract event ID from message content (e.g., "!promotion-upload event:123456")
                import re
                event_match = re.search(r'event:(\w+)', message.content.lower())
                if not event_match:
                    await message.reply("❌ Please specify an event ID in your message (e.g., `!promotion-upload event:123456`).")
                    continue
                
                event_id = event_match.group(1)
                
                # Validate event exists
                try:
                    event_message_id = int(event_id)
                    if event_message_id not in self.active_events:
                        await message.reply(f"❌ Event {event_id} not found!")
                        continue
                    
                    event_data = self.active_events[event_message_id]
                except (ValueError, KeyError):
                    await message.reply(f"❌ Invalid event ID: {event_id}")
                    continue
                
                # Download the image to the promotion directory
                local_path = await self._download_image(
                    attachment=attachment,
                    guild_id=guild_id,
                    user_id=user_id,
                    event_id=event_id,  # Special directory for promotion images
                    category="promotion"
                )
                
                if not local_path:
                    await message.reply("❌ Failed to save the promotional image. Please try again.")
                    continue
                
                # Create CloudEvent for promotion image upload
                from tlt.adapters.discord_adapter.clients.tlt_client import tlt_client
                
                cloudevent_id = await tlt_client.send_promotion_image(
                    guild_id=guild_id,
                    channel_id=str(message.channel.id),
                    user_id=user_id,
                    user_name=message.author.display_name,
                    event_id=event_id,
                    image_url=attachment.url,
                    local_path=str(local_path),
                    event_data=event_data,
                    metadata={
                        "source": "discord_promotion_message_upload",
                        "message_id": str(message.id),
                        "event_topic": event_data.get("topic", "Unknown Event"),
                        "filename": attachment.filename,
                        "content_type": attachment.content_type,
                        "size": attachment.size,
                        "upload_method": "message_command"
                    }
                )
                
                if cloudevent_id:
                    logger.info(f"Promotion image CloudEvent sent: {cloudevent_id}, event: {event_id}, file: {attachment.filename}")
                    
                    # Cross-post the promotional image to the RSVP thread with Gen-Z vibe
                    await self._cross_post_to_rsvp_thread(message, attachment, event_data, event_message_id)
                    
                    # Send confirmation with reaction and reply
                    await message.add_reaction("📸")
                    await message.reply(
                        f"🎉 **Promotion Image Uploaded!**\n\n"
                        f"📋 **Event:** {event_data.get('topic', 'Unknown')}\n"
                        f"📁 **File:** {attachment.filename}\n"
                        f"💾 **Size:** {attachment.size:,} bytes\n"
                        f"🆔 **CloudEvent ID:** `{cloudevent_id[:8]}...`\n\n"
                        f"⏳ The AI agent is processing your promotional image and adding it to the event's reference photos for vibe checking!\n\n"
                        f"🔥 **Plus:** I've shared this fire content in the RSVP thread to get everyone hyped! 📸✨"
                    )
                else:
                    await message.reply("❌ Failed to process promotional image. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error handling promotion image upload: {e}")
            await message.reply("❌ There was an error processing your promotion image. Please try again later.")

# Create a singleton instance
bot = DiscordBot()