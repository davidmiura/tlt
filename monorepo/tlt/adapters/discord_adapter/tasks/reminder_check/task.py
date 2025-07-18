import discord
from discord.ext import tasks
from typing import TYPE_CHECKING
from datetime import datetime, timezone
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class ReminderCheckTask:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
        self.task_loop = None
    
    def start(self):
        """Start the reminder check task"""
        if self.task_loop is None:
            self.task_loop = tasks.loop(minutes=5)(self._reminder_check)
            self.task_loop.start()
    
    def stop(self):
        """Stop the reminder check task"""
        if self.task_loop:
            self.task_loop.stop()
            self.task_loop = None
    
    async def _reminder_check(self):
        """Check and send due reminders"""
        now = datetime.now(timezone.utc)
        due_reminders = []
        
        for reminder_id, reminder in self.bot_instance.active_reminders.items():
            if reminder.get("status") == "pending":
                reminder_time_str = reminder.get("reminder_time")
                if reminder_time_str:
                    try:
                        # Parse reminder_time string to datetime
                        if isinstance(reminder_time_str, str):
                            reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                        else:
                            reminder_time = reminder_time_str
                        
                        # Check if reminder is due
                        if reminder_time <= now:
                            due_reminders.append(reminder_id)
                    except (ValueError, TypeError) as e:
                        logger.error(f"Failed to parse reminder_time for reminder {reminder_id}: {e}")
                        # Mark invalid reminder as failed
                        reminder["status"] = "failed"
                
        for reminder_id in due_reminders:
            await self.bot_instance.send_reminder(reminder_id)