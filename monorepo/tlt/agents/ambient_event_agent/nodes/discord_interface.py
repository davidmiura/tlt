"""Discord interface node for ambient event agent"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from tlt.agents.ambient_event_agent.nodes.base import BaseNode
from tlt.agents.ambient_event_agent.state.state import AgentState, AgentStatus, MessageToSend, MessagePriority

class DiscordInterfaceNode(BaseNode):
    """Handle Discord message sending and interface operations"""
    
    def __init__(self):
        super().__init__("discord_interface")
        self.rate_limit_window = 60  # seconds
        self.max_messages_per_window = 10
        self.recent_messages = []
    
    async def execute(self, state: AgentState) -> AgentState:
        """Process pending Discord messages"""
        self.log_execution(state, "Processing Discord messages")
        
        try:
            self.update_state_metadata(state, {
                "status": AgentStatus.PROCESSING,
                "processing_step": "discord_messaging"
            })
            
            # Check rate limits
            self._cleanup_rate_limit_tracking()
            
            # Process pending messages
            sent_count = await self._process_pending_messages(state)
            
            # Update status
            if sent_count > 0:
                self.log_execution(state, f"Sent {sent_count} Discord messages")
            
            self.update_state_metadata(state, {
                "processing_step": "discord_complete"
            })
            
        except Exception as e:
            self.handle_error(state, e, "Discord messaging")
            state["status"] = AgentStatus.ERROR
        
        return state
    
    async def _process_pending_messages(self, state: AgentState) -> int:
        """Process all pending messages respecting rate limits"""
        sent_count = 0
        messages_to_remove = []
        
        for i, message in enumerate(state["pending_messages"]):
            # Check if we can send this message
            if not self._can_send_message(message):
                continue
            
            # Check if it's time to send (for scheduled messages)
            if message.scheduled_time and message.scheduled_time > datetime.now(timezone.utc):
                continue
            
            # Send the message
            success = await self._send_discord_message(state, message)
            
            if success:
                sent_count += 1
                messages_to_remove.append(i)
                self._track_sent_message(message)
                
                # Respect rate limits
                if sent_count >= self.max_messages_per_window:
                    self.log_execution(state, "Rate limit reached, deferring remaining messages")
                    break
        
        # Remove sent messages (in reverse order to maintain indices)
        for i in reversed(messages_to_remove):
            state["pending_messages"].pop(i)
        
        return sent_count
    
    async def _send_discord_message(self, state: AgentState, message: MessageToSend) -> bool:
        """Send a single Discord message"""
        try:
            # In a real implementation, this would:
            # 1. Connect to Discord adapter
            # 2. Send message via Discord API
            # 3. Handle Discord-specific formatting
            # 4. Manage embeds, attachments, etc.
            
            # For now, simulate sending
            self.log_execution(state, f"Sending message to channel {message.channel_id}: {message.content[:10]}...")
            
            # Simulate network delay
            await asyncio.sleep(0.1)
            
            # Log the message send for debugging
            if state["debug_mode"]:
                self.add_system_message(state, f"Sent Discord message: {message.content}")
            
            return True
            
        except Exception as e:
            self.log_execution(state, f"Failed to send message {message.message_id}: {e}", "error")
            return False
    
    def _can_send_message(self, message: MessageToSend) -> bool:
        """Check if we can send a message based on rate limits"""
        now = datetime.now(timezone.utc)
        
        # Count recent messages
        recent_count = len([
            msg for msg in self.recent_messages 
            if (now - msg["timestamp"]).total_seconds() < self.rate_limit_window
        ])
        
        # Apply priority-based rate limiting
        if message.priority == MessagePriority.URGENT:
            # Urgent messages can bypass normal rate limits
            return recent_count < self.max_messages_per_window * 2
        elif message.priority == MessagePriority.HIGH:
            return recent_count < self.max_messages_per_window * 1.5
        else:
            return recent_count < self.max_messages_per_window
    
    def _track_sent_message(self, message: MessageToSend):
        """Track sent message for rate limiting"""
        self.recent_messages.append({
            "message_id": message.message_id,
            "timestamp": datetime.now(timezone.utc),
            "channel_id": message.channel_id,
            "priority": message.priority
        })
    
    def _cleanup_rate_limit_tracking(self):
        """Clean up old rate limit tracking data"""
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - (self.rate_limit_window * 2)  # Keep extra history
        
        self.recent_messages = [
            msg for msg in self.recent_messages
            if msg["timestamp"].timestamp() > cutoff
        ]
    
    async def send_immediate_message(self, state: AgentState, channel_id: str, content: str, priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Send a message immediately, bypassing the queue"""
        message = MessageToSend(
            channel_id=channel_id,
            content=content,
            priority=priority
        )
        
        if self._can_send_message(message):
            success = await self._send_discord_message(state, message)
            if success:
                self._track_sent_message(message)
            return success
        else:
            # Add to queue if rate limited
            state["pending_messages"].append(message)
            return False
    
    def format_event_message(self, event_context: dict, message_type: str) -> str:
        """Format event-related messages for Discord"""
        if message_type == "reminder_1_day":
            return f"🗓️ **Reminder**: {event_context['title']} is tomorrow at {event_context.get('start_time', 'TBD')}!"
        
        elif message_type == "reminder_day_of":
            return f"📅 **Today**: {event_context['title']} starts in a few hours! Don't forget to join us."
        
        elif message_type == "event_starting":
            location_text = f" at {event_context['location']}" if event_context.get('location') else ""
            return f"🎉 **Starting Now**: {event_context['title']}{location_text} is beginning!"
        
        elif message_type == "followup":
            return f"✨ Thanks for joining {event_context['title']}! We hope you had a great time. Share your photos and memories!"
        
        elif message_type == "rsvp_summary":
            emoji_summary = event_context.get('emoji_summary', {})
            summary_text = ", ".join([f"{emoji}: {count}" for emoji, count in emoji_summary.items()])
            return f"📊 **RSVP Update for {event_context['title']}**: {summary_text}"
        
        else:
            return f"ℹ️ Update about {event_context['title']}"