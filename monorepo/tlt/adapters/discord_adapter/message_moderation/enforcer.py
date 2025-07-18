import discord
from typing import TYPE_CHECKING
import re
import logging

if TYPE_CHECKING:
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot

logger = logging.getLogger(__name__)

class MessageModerationEnforcer:
    def __init__(self, bot_instance: 'DiscordBot'):
        self.bot_instance = bot_instance
    
    async def on_message(self, message: discord.Message):
        """Handle messages in event threads"""
        if message.author.bot:
            return
            
        # Check if message is in an event thread
        if hasattr(message.channel, 'parent') and message.channel.parent:
            parent_id = message.channel.parent.id
            
            # Find the event associated with this thread
            event_message_id = None
            for msg_id, thread_id in self.bot_instance.event_threads.items():
                if thread_id == message.channel.id:
                    event_message_id = msg_id
                    break
                    
            if event_message_id and event_message_id in self.bot_instance.active_events:
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