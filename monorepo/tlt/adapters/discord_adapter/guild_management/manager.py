import discord
from typing import Dict, Optional, TYPE_CHECKING
from datetime import datetime, timezone
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class GuildManager:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild"""
        logger.info(f'Joined new guild: {guild.name} (id: {guild.id})')
        self.bot_instance.guild_settings[guild.id] = {
            "name": guild.name,
            "joined_at": discord.utils.utcnow(),
            "settings": {}
        }
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild"""
        logger.info(f'Left guild: {guild.name} (id: {guild.id})')
        if guild.id in self.bot_instance.guild_settings:
            del self.bot_instance.guild_settings[guild.id]
    
    def get_guild_settings(self, guild_id: int) -> Optional[Dict]:
        """Get settings for a specific guild"""
        return self.bot_instance.guild_settings.get(guild_id)
    
    def update_guild_settings(self, guild_id: int, settings: Dict):
        """Update settings for a specific guild"""
        if guild_id in self.bot_instance.guild_settings:
            self.bot_instance.guild_settings[guild_id]["settings"].update(settings)
            return True
        return False
    
    def is_guild_registered(self, guild_id: int) -> bool:
        """Check if guild is registered"""
        return guild_id in self.bot_instance.registered_guilds
    
    async def register_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Register a guild for TLT events"""
        from tlt.adapters.discord_adapter.permissions.checker import PermissionChecker
        permission_checker = PermissionChecker(self.bot_instance)
        
        if not permission_checker.is_admin(admin):
            return False
        
        self.bot_instance.registered_guilds[guild.id] = {
            "name": guild.name,
            "registered_by": admin.id,
            "registered_at": datetime.now(timezone.utc),
            "settings": {
                "event_channel": None,
                "reminder_times": [24, 2, 0.5]  # hours before event
            }
        }
        logger.info(f"Guild {guild.name} registered by {admin.name}")
        return True
    
    async def deregister_guild(self, guild: discord.Guild, admin: discord.Member) -> bool:
        """Deregister a guild from TLT events"""
        from tlt.adapters.discord_adapter.permissions.checker import PermissionChecker
        permission_checker = PermissionChecker(self.bot_instance)
        
        if not permission_checker.is_admin(admin) or guild.id not in self.bot_instance.registered_guilds:
            return False
        
        # Clean up active events and reminders
        events_to_remove = [msg_id for msg_id, event in self.bot_instance.active_events.items() 
                          if event.get("guild_id") == guild.id]
        for msg_id in events_to_remove:
            del self.bot_instance.active_events[msg_id]
        
        reminders_to_remove = [r_id for r_id, reminder in self.bot_instance.active_reminders.items() 
                             if self.bot_instance.active_events.get(reminder.get("message_id", 0), {}).get("guild_id") == guild.id]
        for r_id in reminders_to_remove:
            del self.bot_instance.active_reminders[r_id]
        
        del self.bot_instance.registered_guilds[guild.id]
        logger.info(f"Guild {guild.name} deregistered by {admin.name}")
        return True