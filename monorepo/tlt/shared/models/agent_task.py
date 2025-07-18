"""Agent Task model for TLT Service - enhanced to support direct IncomingEvent conversion"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventTriggerType(str, Enum):
    """Types of event triggers"""
    DISCORD_MESSAGE = "discord_message"
    TIMER_TRIGGER = "timer_trigger"
    RSVP_REMINDER = "rsvp_reminder"
    EVENT_FOLLOWUP = "event_followup"
    MANUAL_TRIGGER = "manual_trigger"
    CREATE_EVENT = "create_event"
    CLOUDEVENT = "cloudevent"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DiscordContext(BaseModel):
    """Discord-specific context"""
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    user_id: Optional[str] = None
    message_id: Optional[str] = None
    thread_id: Optional[str] = None


class TimerContext(BaseModel):
    """Timer-specific context"""
    timer_type: str  # "1_day_before", "day_of", "event_time", "followup"
    event_id: str
    scheduled_time: datetime


class EventContext(BaseModel):
    """Context information about an event"""
    event_id: str
    event_title: str
    event_description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    created_by: str
    rsvp_count: int = 0
    emoji_summary: Dict[str, int] = Field(default_factory=dict)


class AgentTask(BaseModel):
    """Represents a task for the ambient event agent - enhanced to support direct IncomingEvent conversion"""
    
    # Core task fields (from TLT Service)
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task to execute")
    data: Dict[str, Any] = Field(..., description="Task data payload")
    priority: str = Field("normal", description="Task priority level")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current task status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error: Optional[str] = Field(None, description="Error message if task failed")
    
    # Additional fields for IncomingEvent compatibility
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Event identifier for IncomingEvent")
    trigger_type: EventTriggerType = Field(EventTriggerType.CLOUDEVENT, description="Event trigger type")
    message_priority: MessagePriority = Field(MessagePriority.NORMAL, description="Message priority")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    
    # Context fields (optional)
    discord_context: Optional[DiscordContext] = Field(None, description="Discord-specific context")
    timer_context: Optional[TimerContext] = Field(None, description="Timer-specific context")
    event_context: Optional[EventContext] = Field(None, description="Event-specific context")
    
    # Metadata field for additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def mark_processing(self) -> None:
        """Mark task as processing"""
        self.status = TaskStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)
        
    def mark_completed(self, result: Dict[str, Any]) -> None:
        """Mark task as completed with result"""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.now(timezone.utc)
        
    def mark_failed(self, error: str) -> None:
        """Mark task as failed with error message"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.updated_at = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "data": self.data,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "error": self.error,
            "event_id": self.event_id,
            "trigger_type": self.trigger_type.value,
            "message_priority": self.message_priority.value,
            "timestamp": self.timestamp.isoformat(),
            "discord_context": self.discord_context.dict() if self.discord_context else None,
            "timer_context": self.timer_context.dict() if self.timer_context else None,
            "event_context": self.event_context.dict() if self.event_context else None,
            "metadata": self.metadata
        }
    
    def to_incoming_event_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by IncomingEvent"""
        return {
            "trigger_type": self.trigger_type.value,
            "priority": self.message_priority.value,
            "data": self.data,
            "metadata": self.metadata
        }