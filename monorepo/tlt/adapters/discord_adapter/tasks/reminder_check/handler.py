import discord
from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class ReminderHandler:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def send_reminder(self, reminder_id: str):
        """Send a reminder"""
        try:
            reminder = self.bot_instance.active_reminders.get(reminder_id)
            if not reminder:
                return
                
            event = self.bot_instance.active_events.get(reminder["message_id"])
            if not event:
                return
                
            guild = self.bot_instance.get_guild(event["guild_id"])
            if not guild:
                return
                
            # Send to RSVP thread instead of main channel
            target_channel = None
            
            # Debug: Log event data to understand the structure
            logger.info(f"Event data for reminder {reminder_id}: {event}")
            
            # First try to get the RSVP thread (public_thread_id)
            if "public_thread_id" in event:
                public_thread_id = event["public_thread_id"]
                logger.info(f"Attempting to find RSVP thread with ID: {public_thread_id}")
                target_channel = guild.get_thread(public_thread_id)
                if target_channel:
                    logger.info(f"✅ Found RSVP thread: {target_channel.name} (ID: {target_channel.id})")
                else:
                    logger.warning(f"❌ RSVP thread {public_thread_id} not found in guild threads")
                    # Try to fetch thread from channel if it's not in cache
                    main_channel = guild.get_channel(event["channel_id"])
                    if main_channel:
                        try:
                            target_channel = await main_channel.fetch_thread(public_thread_id)
                            logger.info(f"✅ Fetched RSVP thread from channel: {target_channel.name}")
                        except discord.NotFound:
                            logger.warning(f"❌ RSVP thread {public_thread_id} no longer exists")
                        except Exception as e:
                            logger.error(f"❌ Error fetching RSVP thread: {e}")
            else:
                logger.warning(f"❌ No public_thread_id found in event data")
            
            # Fallback to main channel if RSVP thread not found
            if not target_channel:
                target_channel = guild.get_channel(event["channel_id"])
                logger.warning(f"⚠️ RSVP thread not available, falling back to main channel: {target_channel.name if target_channel else 'None'}")
            
            if target_channel:
                embed = discord.Embed(
                    title="⏰ Event Reminder",
                    description=f"**{event['topic']}** is coming up!",
                    color=discord.Color.orange()
                )
                embed.add_field(name="📍 Location", value=event['location'])
                embed.add_field(name="🕐 Time", value=event['time'])
                embed.add_field(name="⏳ Reminder", value=reminder["message"])
                
                await target_channel.send(embed=embed)
                
            reminder["status"] = "sent"
            logger.info(f"Sent reminder {reminder_id}")
            
        except Exception as e:
            logger.error(f"Error sending reminder {reminder_id}: {e}")
            reminder["status"] = "failed"
    
    async def schedule_event_reminders(self, message_id: int, event_time_str: str):
        """Schedule automatic reminders for an event"""
        # This is a simple implementation - in production you'd want better time parsing
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