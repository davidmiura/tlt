from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import uuid

class PhotoStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    CURATED = "curated"

class PhotoType(str, Enum):
    USER_SUBMISSION = "user_submission"
    PRE_EVENT_CURATION = "pre_event_curation"

class PhotoQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNUSABLE = "unusable"

class PhotoRelevance(str, Enum):
    HIGHLY_RELEVANT = "highly_relevant"
    RELEVANT = "relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"
    NOT_RELEVANT = "not_relevant"

class PhotoSubmission(BaseModel):
    photo_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    user_id: str
    photo_url: str
    photo_type: PhotoType = PhotoType.USER_SUBMISSION
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: PhotoStatus = PhotoStatus.SUBMITTED
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PhotoAnalysis(BaseModel):
    photo_id: str
    quality_score: float = Field(ge=0.0, le=1.0)
    quality_rating: PhotoQuality
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_rating: PhotoRelevance
    size_check: bool
    content_analysis: str
    similarity_scores: Dict[str, float] = Field(default_factory=dict)  # similarity to pre-event photos
    overall_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventPhotoConfig(BaseModel):
    event_id: str
    activated: bool = False
    rate_limit_hours: int = 1  # photos per hour per user
    max_hours_after_event: int = 24  # hours after event start to accept photos
    event_start_time: Optional[datetime] = None
    admin_user_id: str
    pre_event_photos: List[str] = Field(default_factory=list)  # URLs of curated pre-event photos
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SlideshowPhoto(BaseModel):
    photo_id: str
    photo_url: str
    score: float
    caption: Optional[str] = None
    user_id: str
    submitted_at: datetime

class Slideshow(BaseModel):
    slideshow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    photos: List[SlideshowPhoto]
    total_submissions: int
    accepted_count: int
    rejected_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PhotoSubmissionResponse(BaseModel):
    success: bool
    photo_id: Optional[str] = None
    message: str
    rate_limit_remaining: Optional[int] = None
    next_allowed_submission: Optional[datetime] = None

class RateLimitInfo(BaseModel):
    user_id: str
    event_id: str
    submissions_this_hour: int
    last_submission: datetime
    next_allowed: datetime

class PhotoProcessingState(BaseModel):
    photo_id: str
    current_step: str
    progress: float = Field(ge=0.0, le=1.0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

# Tool Result Models for UserStateManager
class SubmitPhotoDmResult(BaseModel):
    success: bool
    photo_id: Optional[str] = None
    message: str
    rate_limit_remaining: Optional[int] = None
    next_allowed_submission: Optional[str] = None
    vibe_check: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    photo_url: str
    metadata: Optional[Dict[str, Any]] = None

class ActivatePhotoCollectionResult(BaseModel):
    success: bool
    message: str
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str
    rate_limit_hours: int
    max_hours_after_event: int
    event_start_time: Optional[str] = None
    pre_event_photos: Optional[List[str]] = None

class DeactivatePhotoCollectionResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str

class UpdatePhotoSettingsResult(BaseModel):
    success: bool
    message: str
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str
    rate_limit_hours: Optional[int] = None
    max_hours_after_event: Optional[int] = None
    event_start_time: Optional[str] = None

class AddPreEventPhotosResult(BaseModel):
    success: bool
    message: str
    total_photos: Optional[int] = None
    new_photos_added: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str
    photo_urls: List[str]

class GetPhotoStatusResult(BaseModel):
    success: bool
    message: Optional[str] = None
    photo_id: Optional[str] = None
    status: Optional[str] = None
    submitted_at: Optional[str] = None
    user_id: Optional[str] = None
    event_id: Optional[str] = None
    processing: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetEventPhotoSummaryResult(BaseModel):
    success: bool
    message: Optional[str] = None
    event_id: Optional[str] = None
    activated: Optional[bool] = None
    total_submissions: Optional[int] = None
    status_breakdown: Optional[Dict[str, int]] = None
    approved_count: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    time_window: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GenerateEventSlideshowResult(BaseModel):
    success: bool
    message: Optional[str] = None
    slideshow_id: Optional[str] = None
    event_id: Optional[str] = None
    photos: Optional[List[Dict[str, Any]]] = None
    total_submissions: Optional[int] = None
    accepted_count: Optional[int] = None
    rejected_count: Optional[int] = None
    created_at: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetUserPhotoHistoryResult(BaseModel):
    success: bool
    message: Optional[str] = None
    user_id: Optional[str] = None
    total_submissions: Optional[int] = None
    submissions: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: Optional[str] = None