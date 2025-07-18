import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class PermissionChecker:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if member is admin"""
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild