import uuid
from loguru import logger
import httpx
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from tlt.mcp_services.photo_vibe_check.models import (
    PhotoSubmission, PhotoAnalysis, EventPhotoConfig, Slideshow, SlideshowPhoto,
    PhotoSubmissionResponse, RateLimitInfo, PhotoProcessingState,
    PhotoStatus, PhotoType, PhotoQuality, PhotoRelevance
)

# Using loguru logger imported above

class PhotoVibeCheckService:
    def __init__(self, event_manager_url: str = "http://localhost:8004"):
        # In-memory storage (in production, use database)
        self.photo_submissions: Dict[str, PhotoSubmission] = {}
        self.photo_analyses: Dict[str, PhotoAnalysis] = {}
        self.event_configs: Dict[str, EventPhotoConfig] = {}
        self.slideshows: Dict[str, Slideshow] = {}
        self.rate_limits: Dict[str, RateLimitInfo] = {}  # key: f"{user_id}_{event_id}"
        self.processing_states: Dict[str, PhotoProcessingState] = {}
        
        self.event_manager_url = event_manager_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def validate_rsvp(self, event_id: str, user_id: str) -> bool:
        """Validate that user has RSVP'd for the event"""
        try:
            response = await self.client.get(
                f"{self.event_manager_url}/event/{event_id}/rsvps"
            )
            if response.status_code == 200:
                event_data = response.json()
                rsvps = event_data.get("rsvps", [])
                
                # Check if user has any RSVP for this event
                user_rsvp = next((rsvp for rsvp in rsvps if rsvp["user_id"] == user_id), None)
                if user_rsvp:
                    # Consider attending, maybe, and tentative as valid for photo submission
                    valid_statuses = ["attending", "maybe", "tentative"]
                    return user_rsvp["status"] in valid_statuses
                    
            return False
        except Exception as e:
            logger.error(f"Error validating RSVP: {e}")
            return False
    
    def check_rate_limit(self, user_id: str, event_id: str) -> Tuple[bool, Optional[RateLimitInfo]]:
        """Check if user is within rate limit for photo submissions"""
        rate_key = f"{user_id}_{event_id}"
        config = self.event_configs.get(event_id)
        
        if not config:
            return False, None
            
        rate_limit_hours = config.rate_limit_hours
        now = datetime.now(timezone.utc)
        
        if rate_key not in self.rate_limits:
            # First submission, allow it
            return True, None
            
        rate_info = self.rate_limits[rate_key]
        time_since_last = now - rate_info.last_submission
        
        if time_since_last.total_seconds() >= rate_limit_hours * 3600:
            # Enough time has passed
            return True, rate_info
        else:
            # Still within rate limit
            next_allowed = rate_info.last_submission + timedelta(hours=rate_limit_hours)
            rate_info.next_allowed = next_allowed
            return False, rate_info
    
    def check_time_window(self, event_id: str) -> bool:
        """Check if current time is within the allowed submission window"""
        config = self.event_configs.get(event_id)
        if not config or not config.activated:
            return False
            
        if not config.event_start_time:
            # If no start time set, assume submissions are always allowed when activated
            return True
            
        now = datetime.now(timezone.utc)
        max_end_time = config.event_start_time + timedelta(hours=config.max_hours_after_event)
        
        # Allow submissions from event start time until max_hours_after_event
        return config.event_start_time <= now <= max_end_time
    
    def update_rate_limit(self, user_id: str, event_id: str):
        """Update rate limit tracking for user"""
        rate_key = f"{user_id}_{event_id}"
        now = datetime.now(timezone.utc)
        
        config = self.event_configs.get(event_id)
        if not config:
            return
            
        if rate_key in self.rate_limits:
            rate_info = self.rate_limits[rate_key]
            rate_info.submissions_this_hour += 1
            rate_info.last_submission = now
        else:
            rate_info = RateLimitInfo(
                user_id=user_id,
                event_id=event_id,
                submissions_this_hour=1,
                last_submission=now,
                next_allowed=now + timedelta(hours=config.rate_limit_hours)
            )
            self.rate_limits[rate_key] = rate_info
    
    async def submit_photo(
        self, 
        event_id: str, 
        user_id: str, 
        photo_url: str,
        metadata: Optional[Dict] = None
    ) -> PhotoSubmissionResponse:
        """Submit a photo for processing"""
        try:
            # Check if event photo collection is activated
            config = self.event_configs.get(event_id)
            # if not config or not config.activated:
            #     return PhotoSubmissionResponse(
            #         success=False,
            #         message="Photo submissions are not currently active for this event"
            #     )
            
            # # Check time window
            # if not self.check_time_window(event_id):
            #     return PhotoSubmissionResponse(
            #         success=False,
            #         message="Photo submissions are outside the allowed time window"
            #     )
            
            # # Validate RSVP
            # has_rsvp = await self.validate_rsvp(event_id, user_id)
            # if not has_rsvp:
            #     return PhotoSubmissionResponse(
            #         success=False,
            #         message="Only users who have RSVP'd can submit photos"
            #     )
            
            # # Check rate limit
            # within_limit, rate_info = self.check_rate_limit(user_id, event_id)
            # if not within_limit:
            #     return PhotoSubmissionResponse(
            #         success=False,
            #         message=f"Rate limit exceeded. Next submission allowed at {rate_info.next_allowed}",
            #         next_allowed_submission=rate_info.next_allowed
            #     )
            
            # Create photo submission
            photo_submission = PhotoSubmission(
                event_id=event_id,
                user_id=user_id,
                photo_url=photo_url,
                metadata=metadata or {}
            )
            
            self.photo_submissions[photo_submission.photo_id] = photo_submission
            
            # # Update rate limit
            # self.update_rate_limit(user_id, event_id)
            
            # Create processing state
            processing_state = PhotoProcessingState(
                photo_id=photo_submission.photo_id,
                current_step="submitted",
                progress=0.1
            )
            self.processing_states[photo_submission.photo_id] = processing_state
            
            logger.info(f"Photo submitted: {photo_submission.photo_id} by user {user_id} for event {event_id}")
            
            return PhotoSubmissionResponse(
                success=True,
                photo_id=photo_submission.photo_id,
                message="Photo submitted successfully and queued for processing"
            )
            
        except Exception as e:
            logger.error(f"Error submitting photo: {e}")
            return PhotoSubmissionResponse(
                success=False,
                message="Internal server error"
            )
    
    def create_event_config(
        self, 
        event_id: str, 
        admin_user_id: str,
        activated: bool = False,
        rate_limit_hours: int = 1,
        max_hours_after_event: int = 24,
        event_start_time: Optional[datetime] = None,
        pre_event_photos: Optional[List[str]] = None
    ) -> EventPhotoConfig:
        """Create or update event photo configuration"""
        config = EventPhotoConfig(
            event_id=event_id,
            activated=activated,
            rate_limit_hours=rate_limit_hours,
            max_hours_after_event=max_hours_after_event,
            event_start_time=event_start_time,
            admin_user_id=admin_user_id,
            pre_event_photos=pre_event_photos or []
        )
        
        self.event_configs[event_id] = config
        logger.info(f"Created event config for {event_id} by admin {admin_user_id}")
        
        return config
    
    def update_event_config(
        self,
        event_id: str,
        admin_user_id: str,
        **updates
    ) -> Optional[EventPhotoConfig]:
        """Update event configuration (admin only)"""
        config = self.event_configs.get(event_id)
        if not config:
            return None
            
        if config.admin_user_id != admin_user_id:
            raise ValueError("Only the event admin can update configuration")
        
        # Update allowed fields
        allowed_updates = [
            'activated', 'rate_limit_hours', 'max_hours_after_event', 
            'event_start_time', 'pre_event_photos'
        ]
        
        for key, value in updates.items():
            if key in allowed_updates and hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Updated event config for {event_id} by admin {admin_user_id}")
        return config
    
    def get_event_config(self, event_id: str) -> Optional[EventPhotoConfig]:
        """Get event photo configuration"""
        return self.event_configs.get(event_id)
    
    def get_photo_submission(self, photo_id: str) -> Optional[PhotoSubmission]:
        """Get photo submission by ID"""
        return self.photo_submissions.get(photo_id)
    
    def get_photo_analysis(self, photo_id: str) -> Optional[PhotoAnalysis]:
        """Get photo analysis by ID"""
        return self.photo_analyses.get(photo_id)
    
    def get_processing_state(self, photo_id: str) -> Optional[PhotoProcessingState]:
        """Get photo processing state"""
        return self.processing_states.get(photo_id)
    
    def get_event_submissions(self, event_id: str) -> List[PhotoSubmission]:
        """Get all photo submissions for an event"""
        return [
            submission for submission in self.photo_submissions.values()
            if submission.event_id == event_id
        ]
    
    def get_user_submissions(self, user_id: str, event_id: Optional[str] = None) -> List[PhotoSubmission]:
        """Get all photo submissions for a user, optionally filtered by event"""
        submissions = [
            submission for submission in self.photo_submissions.values()
            if submission.user_id == user_id
        ]
        
        if event_id:
            submissions = [s for s in submissions if s.event_id == event_id]
            
        return submissions
    
    def store_photo_analysis(self, analysis: PhotoAnalysis):
        """Store photo analysis results"""
        self.photo_analyses[analysis.photo_id] = analysis
        
        # Update photo submission status
        if analysis.photo_id in self.photo_submissions:
            submission = self.photo_submissions[analysis.photo_id]
            if analysis.overall_score >= 0.7:  # Threshold for approval
                submission.status = PhotoStatus.APPROVED
            else:
                submission.status = PhotoStatus.REJECTED
        
        # Update processing state
        if analysis.photo_id in self.processing_states:
            processing_state = self.processing_states[analysis.photo_id]
            processing_state.current_step = "analyzed"
            processing_state.progress = 0.8
            processing_state.updated_at = datetime.now(timezone.utc)
    
    def create_slideshow(self, event_id: str) -> Optional[Slideshow]:
        """Create slideshow from approved photos"""
        config = self.event_configs.get(event_id)
        if not config:
            return None
        
        # Get all submissions for this event
        submissions = self.get_event_submissions(event_id)
        approved_submissions = [
            s for s in submissions 
            if s.status == PhotoStatus.APPROVED
        ]
        
        if not approved_submissions:
            return None
        
        # Get analyses and sort by score
        slideshow_photos = []
        for submission in approved_submissions:
            analysis = self.photo_analyses.get(submission.photo_id)
            if analysis:
                slideshow_photo = SlideshowPhoto(
                    photo_id=submission.photo_id,
                    photo_url=submission.photo_url,
                    score=analysis.overall_score,
                    user_id=submission.user_id,
                    submitted_at=submission.submitted_at
                )
                slideshow_photos.append(slideshow_photo)
        
        # Sort by score (highest first)
        slideshow_photos.sort(key=lambda x: x.score, reverse=True)
        
        slideshow = Slideshow(
            event_id=event_id,
            photos=slideshow_photos,
            total_submissions=len(submissions),
            accepted_count=len(approved_submissions),
            rejected_count=len(submissions) - len(approved_submissions)
        )
        
        self.slideshows[slideshow.slideshow_id] = slideshow
        logger.info(f"Created slideshow {slideshow.slideshow_id} for event {event_id} with {len(slideshow_photos)} photos")
        
        return slideshow
    
    def get_slideshow(self, slideshow_id: str) -> Optional[Slideshow]:
        """Get slideshow by ID"""
        return self.slideshows.get(slideshow_id)
    
    def get_event_slideshow(self, event_id: str) -> Optional[Slideshow]:
        """Get slideshow for an event"""
        for slideshow in self.slideshows.values():
            if slideshow.event_id == event_id:
                return slideshow
        return None