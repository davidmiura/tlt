import discord
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class ReminderBridgeHandlers:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def send_reminder(self, reminder_id: str):
        """Delegate to reminder handler"""
        await self.bot_instance.reminder_handler.send_reminder(reminder_id)
    
    async def schedule_event_reminders(self, message_id: int, event_time_str: str):
        """Delegate to reminder handler"""
        await self.bot_instance.reminder_handler.schedule_event_reminders(message_id, event_time_str)