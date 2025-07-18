from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# RSVP Models - focused on user RSVP operations
class RSVPCreate(BaseModel):
    event_id: str
    user_id: str
    emoji: str  # Single emoji response only
    response_time: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RSVPUpdate(BaseModel):
    emoji: Optional[str] = None  # Update to single emoji only
    response_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class RSVPResponse(BaseModel):
    rsvp_id: str
    event_id: str
    user_id: str
    emoji: str  # Single emoji used for RSVP
    response_time: datetime
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class UserRSVPSummary(BaseModel):
    user_id: str
    total_rsvps: int
    events_by_emoji: Dict[str, List[str]]  # emoji -> list of event_ids
    recent_rsvps: List[RSVPResponse]
    last_updated: datetime

class EventRSVPSummary(BaseModel):
    event_id: str
    total_responses: int
    emoji_breakdown: Dict[str, int]  # emoji -> count
    response_rate: float
    last_updated: datetime
    rsvps: List[RSVPResponse]

class RSVPAnalytics(BaseModel):
    event_id: str
    total_responses: int
    emoji_breakdown: Dict[str, int]  # emoji -> count
    response_timeline: List[Dict[str, Any]]
    peak_response_time: Optional[str] = None
    average_response_time: Optional[float] = None
    most_popular_emoji: Optional[str] = None
    unique_users: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Tool Result Models for UserStateManager
class CreateRsvpResult(BaseModel):
    success: bool
    rsvp: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    emoji: str
    metadata: Optional[Dict[str, Any]] = None

class GetRsvpResult(BaseModel):
    success: bool
    rsvp: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rsvp_id: str

class UpdateRsvpResult(BaseModel):
    success: bool
    rsvp: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rsvp_id: str
    emoji: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DeleteRsvpResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rsvp_id: str

class GetUserRsvpForEventResult(BaseModel):
    success: bool
    rsvp: Optional[Dict[str, Any]] = None
    has_rsvp: bool
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    event_id: str

class GetEventRsvpsResult(BaseModel):
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str

class GetUserRsvpsResult(BaseModel):
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str

class UpdateUserRsvpResult(BaseModel):
    success: bool
    rsvp: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    emoji: str
    metadata: Optional[Dict[str, Any]] = None

class GetRsvpAnalyticsResult(BaseModel):
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str

class ListEventsWithRsvpsResult(BaseModel):
    success: bool
    events: Optional[List[str]] = None
    count: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetRsvpStatsResult(BaseModel):
    success: bool
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProcessRsvpResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    rsvp_type: str
    emoji: str
    metadata: Optional[Dict[str, Any]] = None