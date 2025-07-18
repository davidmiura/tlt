import discord
from discord.ext import commands, tasks
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncio
import re

logger = logging.getLogger(__name__)

# Import TLT command handlers
from tlt.adapters.discord_adapter.commands.tlt.create.modal import EventCreateModal
from tlt.adapters.discord_adapter.commands.tlt.create.handler import EventCreateHandler
from tlt.adapters.discord_adapter.commands.tlt.update.handler import EventUpdateHandler
from tlt.adapters.discord_adapter.commands.tlt.list.handler import EventListHandler
from tlt.adapters.discord_adapter.commands.tlt.delete.handler import EventDeleteHandler
from tlt.adapters.discord_adapter.commands.tlt.info.handler import EventInfoHandler

# Import register/deregister command handlers
from tlt.adapters.discord_adapter.commands.register.handler import RegisterCommandHandler
from tlt.adapters.discord_adapter.commands.deregister.handler import DeregisterCommandHandler

# Import task handlers
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
        self.guild_settings: Dict[int, Dict] = {}
        self.registered_guilds: Dict[int, Dict] = {}
        self.active_events: Dict[int, Dict] = {}
        self.active_reminders: Dict[str, Dict] = {}
        self.experiences: Dict[str, Dict] = {}
        self.event_threads: Dict[int, int] = {}  # message_id -> thread_id
        
        # Initialize task handlers
        self.reminder_check_task = ReminderCheckTask(self)
        self.reminder_handler = ReminderHandler(self)
        
    async def setup_hook(self):
        """Initialize bot settings and load extensions"""
        logger.info("Setting up bot...")
        self.reminder_check_task.start()
        await self.setup_slash_commands()
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild"""
        logger.info(f'Joined new guild: {guild.name} (id: {guild.id})')
        self.guild_settings[guild.id] = {
            "name": guild.name,
            "joined_at": discord.utils.utcnow(),
            "settings": {}
        }
        
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild"""
        logger.info(f'Left guild: {guild.name} (id: {guild.id})')
        if guild.id in self.guild_settings:
            del self.guild_settings[guild.id]
            
    def get_guild_settings(self, guild_id: int) -> Optional[Dict]:
        """Get settings for a specific guild"""
        return self.guild_settings.get(guild_id)
        
    def update_guild_settings(self, guild_id: int, settings: Dict):
        """Update settings for a specific guild"""
        if guild_id in self.guild_settings:
            self.guild_settings[guild_id]["settings"].update(settings)
            return True
        return False
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if member is admin"""
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild
    
    def is_guild_registered(self, guild_id: int) -> bool:
        """Check if guild is registered"""
        return guild_id in self.registered_guilds
    
    async def register_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Register a guild for TLT events"""
        if not self.is_admin(admin):
            return False
        
        self.registered_guilds[guild.id] = {
            "name": guild.name,
            "registered_by": admin.id,
            "registered_at": datetime.utcnow(),
            "settings": {
                "event_channel": None,
                "reminder_times": [24, 2, 0.5]  # hours before event
            }
        }
        logger.info(f"Guild {guild.name} registered by {admin.name}")
        return True
    
    async def deregister_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Deregister a guild from TLT events"""
        if not self.is_admin(admin) or guild.id not in self.registered_guilds:
            return False
        
        # Clean up active events and reminders
        events_to_remove = [msg_id for msg_id, event in self.active_events.items() 
                          if event.get("guild_id") == guild.id]
        for msg_id in events_to_remove:
            del self.active_events[msg_id]
        
        reminders_to_remove = [r_id for r_id, reminder in self.active_reminders.items() 
                             if self.active_events.get(reminder.get("message_id", 0), {}).get("guild_id") == guild.id]
        for r_id in reminders_to_remove:
            del self.active_reminders[r_id]
        
        del self.registered_guilds[guild.id]
        logger.info(f"Guild {guild.name} deregistered by {admin.name}")
        return True

    async def setup_slash_commands(self):
        """Setup slash commands"""
        @self.tree.command(name="tlt", description="Manage TLT events")
        @discord.app_commands.describe(
            action="Action to perform",
            event_id="Event ID for info/update/delete operations"
        )
        async def tlt_command(
            interaction: discord.Interaction,
            action: str,
            event_id: str = None
        ):
            await self.handle_tlt_command(interaction, action, event_id)
            
        @self.tree.command(name="register", description="Register guild for TLT events (Admin only)")
        async def register_command(interaction: discord.Interaction):
            handler = RegisterCommandHandler(self)
            await handler.handle_command(interaction)
            
        @self.tree.command(name="deregister", description="Deregister guild from TLT events (Admin only)")
        async def deregister_command(interaction: discord.Interaction):
            handler = DeregisterCommandHandler(self)
            await handler.handle_command(interaction)


    async def handle_tlt_command(self, interaction: discord.Interaction, action: str, event_id: str):
        """Handle /tlt command"""
        if not self.is_guild_registered(interaction.guild.id):
            await interaction.response.send_message("❌ Guild not registered. Use `/register` first.", ephemeral=True)
            return
            
        action = action.lower()
        
        if action == "create":
            # Show modal for event creation
            modal = EventCreateModal(self)
            await interaction.response.send_modal(modal)
        elif action == "list":
            logger.debug(f"Listing events for guild list_events_command **interaction** {interaction}")
            handler = EventListHandler(self)
            await handler.handle_command(interaction)
        elif action == "update":
            handler = EventUpdateHandler(self)
            await handler.handle_command(interaction)
        elif action == "delete":
            if not event_id:
                await interaction.response.send_message("❌ Event ID required for delete action.", ephemeral=True)
                return
            handler = EventDeleteHandler(self)
            await handler.handle_command(interaction, event_id)
        elif action == "info":
            if not event_id:
                await interaction.response.send_message("❌ Event ID required for info action.", ephemeral=True)
                return
            handler = EventInfoHandler(self)
            await handler.handle_command(interaction, event_id)
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `create`, `list`, `update`, `delete`, or `info`", 
                ephemeral=True
            )

    async def create_event_from_modal(self, interaction: discord.Interaction, topic: str, location: str, time: str):
        """Create a new event from modal submission"""
        handler = EventCreateHandler(self)
        await handler.handle_modal_submission(interaction, topic, location, time)
    
    async def update_event_from_modal(self, interaction: discord.Interaction, message_id: int, topic: str, location: str, time: str):
        """Update an existing event from modal submission"""
        handler = EventUpdateHandler(self)
        await handler.handle_modal_submission(interaction, message_id, topic, location, time)
    
    async def send_reminder(self, reminder_id: str):
        """Delegate to reminder handler"""
        await self.reminder_handler.send_reminder(reminder_id)
    
    async def schedule_event_reminders(self, message_id: int, event_time_str: str):
        """Delegate to reminder handler"""
        await self.reminder_handler.schedule_event_reminders(message_id, event_time_str)

        
        
        
            
        thread = await message.create_thread(
            name=f"RSVP: {topic}",
            auto_archive_duration=10080  # 7 days
        )
        self.event_threads[message.id] = thread.id
        
        # Send thread rules
        rules_embed = discord.Embed(
            title="✨ Vibe Check Zone ✨",
            description="Yo! This thread is emoji-only energy! 🚀\n\n" +
                       "Let’s see that vibe 🫣🎉🪩🧠💃🫨",
            color=discord.Color.magenta()
        )
        await thread.send(embed=rules_embed)
        
        # Schedule automatic reminders
        await self.schedule_event_reminders(message.id, time)








    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction additions"""
        if user.bot:
            return
            
        message_id = reaction.message.id
        if message_id not in self.active_events:
            return
            
        event = self.active_events[message_id]
        emoji = str(reaction.emoji)
        
        # Initialize reactions if needed
        if "reactions" not in event:
            event["reactions"] = {}
        if emoji not in event["reactions"]:
            event["reactions"][emoji] = []
            
        # Add user if not already in list
        if user.id not in event["reactions"][emoji]:
            event["reactions"][emoji].append(user.id)
            logger.info(f'User {user.name} reacted with {emoji} to event: {event["topic"]}')
            
        # Update message embed
        await self.update_event_embed(reaction.message, event)

    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        """Handle reaction removals"""
        if user.bot:
            return
            
        message_id = reaction.message.id
        if message_id not in self.active_events:
            return
            
        event = self.active_events[message_id]
        emoji = str(reaction.emoji)
        
        # Remove user from reaction list
        if "reactions" in event and emoji in event["reactions"]:
            if user.id in event["reactions"][emoji]:
                event["reactions"][emoji].remove(user.id)
                logger.info(f'User {user.name} removed {emoji} reaction from event: {event["topic"]}')
                
        # Update message embed  
        await self.update_event_embed(reaction.message, event)

    async def update_event_embed(self, message: discord.Message, event: Dict):
        """Update event message embed with current reactions"""
        embed = discord.Embed(
            title=f"📅 {event['topic']}",
            description=f"**📍 Location:** {event['location']}\n**🕐 Time:** {event['time']}",
            color=discord.Color.blue()
        )
        
        # Add reaction counts
        reactions = event.get("reactions", {})
        if reactions:
            rsvp_text = ""
            for emoji, users in reactions.items():
                if users:
                    rsvp_text += f"{emoji} {len(users)} "
            if rsvp_text:
                embed.add_field(name="📝 RSVPs", value=rsvp_text.strip(), inline=False)
                
        creator = message.guild.get_member(event["creator_id"])
        if creator:
            embed.set_footer(text=f"Created by {creator.display_name}")
            
        try:
            await message.edit(embed=embed)
        except Exception as e:
            logger.error(f"Error updating embed: {e}")

    async def on_message(self, message: discord.Message):
        """Handle messages in event threads"""
        if message.author.bot:
            return
            
        # Check if message is in an event thread
        if hasattr(message.channel, 'parent') and message.channel.parent:
            parent_id = message.channel.parent.id
            
            # Find the event associated with this thread
            event_message_id = None
            for msg_id, thread_id in self.event_threads.items():
                if thread_id == message.channel.id:
                    event_message_id = msg_id
                    break
                    
            if event_message_id and event_message_id in self.active_events:
                # This is an event thread - check if message contains only emojis
                content = message.content.strip()
                
                # Allow empty messages (could be just reactions)
                if not content:
                    return
                    
                # Check if content is only emojis/reactions
                emoji_pattern = re.compile(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\s]*$')
                
                if not emoji_pattern.match(content):
                    # Delete non-emoji message
                    try:
                        await message.delete()
                        
                        # Send warning to user via DM
                        embed = discord.Embed(
                            title="🚫 Message Deleted",
                            description="Event threads are for **emoji reactions only**.\n\nUse reactions on the main event message to RSVP.",
                            color=discord.Color.red()
                        )
                        
                        try:
                            await message.author.send(embed=embed)
                        except discord.Forbidden:
                            pass  # User has DMs disabled
                            
                        logger.info(f"Deleted non-emoji message from {message.author.name} in event thread")
                        
                    except discord.NotFound:
                        pass  # Message already deleted
                    except Exception as e:
                        logger.error(f"Error deleting message in event thread: {e}")

    async def generate_event_artifact(self, message_id: int):
        """Generate post-event artifact"""
        if message_id not in self.active_events:
            return
            
        event = self.active_events[message_id]
        guild = self.get_guild(event["guild_id"])
        if not guild:
            return
            
        # Get all experiences for this event
        event_experiences = [
            exp for exp in self.experiences.values()
            if exp.get("message_id") == message_id
        ]
        
        # Create artifact embed
        embed = discord.Embed(
            title=f"📸 Event Summary: {event['topic']}",
            description=f"**📍 Location:** {event['location']}\n**🕐 Time:** {event['time']}",
            color=discord.Color.green()
        )
        
        # Add attendance summary
        reactions = event.get("reactions", {})
        attended_count = len(reactions.get("✅", []))
        maybe_count = len(reactions.get("❓", []))
        declined_count = len(reactions.get("❌", []))
        
        embed.add_field(
            name="📊 Attendance",
            value=f"✅ Attended: {attended_count}\n❓ Maybe: {maybe_count}\n❌ Declined: {declined_count}",
            inline=True
        )
        
        # Add experience summary
        if event_experiences:
            total_rating = sum(exp["rating"] for exp in event_experiences)
            avg_rating = total_rating / len(event_experiences)
            embed.add_field(
                name="⭐ Experience Rating",
                value=f"{avg_rating:.1f}/5.0 ({len(event_experiences)} reviews)",
                inline=True
            )
            
            # Add some feedback highlights
            feedback_highlights = [exp["feedback"][:100] + "..." if len(exp["feedback"]) > 100 
                                 else exp["feedback"] for exp in event_experiences[:3]]
            if feedback_highlights:
                embed.add_field(
                    name="💬 Feedback Highlights",
                    value="\n".join([f"• {fb}" for fb in feedback_highlights]),
                    inline=False
                )
        
        embed.set_footer(text=f"Event completed • Generated by TLT Bot")
        
        # Send to original channel
        channel = guild.get_channel(event["channel_id"])
        if channel:
            await channel.send(embed=embed)
            logger.info(f"Generated artifact for event: {event['topic']}")

# Create a singleton instance
bot = DiscordBot()