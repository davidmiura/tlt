from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import uuid

class EventStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Event models - focused on event owner operations
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_by: str
    max_capacity: Optional[int] = None
    require_approval: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    event_id: Optional[str] = None  # Optional event ID (if not provided, UUID will be generated)

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[EventStatus] = None
    max_capacity: Optional[int] = None
    require_approval: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class EventResponse(BaseModel):
    event_id: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: EventStatus
    created_by: str
    max_capacity: Optional[int] = None
    require_approval: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventSummary(BaseModel):
    event_id: str
    title: str
    status: EventStatus
    created_by: str
    start_time: Optional[datetime] = None
    location: Optional[str] = None
    created_at: datetime
    
class EventListResponse(BaseModel):
    events: List[EventSummary]
    total_count: int
    filter_applied: Optional[str] = None
    
class EventAnalytics(BaseModel):
    event_id: str
    title: str
    status: EventStatus
    created_by: str
    created_at: datetime
    days_since_created: int
    is_upcoming: bool
    is_past_due: bool
    capacity_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Tool Result Models for UserStateManager
class CreateEventResult(BaseModel):
    success: bool
    event_id: Optional[str] = None
    message: str
    event: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    guild_id: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_capacity: Optional[int] = None
    require_approval: bool = False
    metadata: Optional[Dict[str, Any]] = None

class GetEventResult(BaseModel):
    success: bool
    event: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: Optional[str] = None
    guild_id: str

class UpdateEventResult(BaseModel):
    success: bool
    event: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    guild_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None
    max_capacity: Optional[int] = None
    require_approval: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class DeleteEventResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    guild_id: str

class ListAllEventsResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    guild_id: str
    status: Optional[str] = None
    limit: int = 100

class GetEventsByCreatorResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    creator_id: str
    user_id: str
    guild_id: str

class GetEventsByStatusResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str
    user_id: str
    guild_id: str

class GetEventAnalyticsResult(BaseModel):
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    guild_id: str

class SearchEventsResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    query: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    guild_id: str
    limit: int = 50

class GetEventStatsResult(BaseModel):
    success: bool
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    guild_id: str

class SaveEventToGuildDataResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    guild_id: str
    user_id: str
    event_data: Dict[str, Any]