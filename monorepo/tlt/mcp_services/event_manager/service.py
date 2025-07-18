import uuid
from loguru import logger
from typing import Dict, List, Optional
from datetime import datetime, timezone

from tlt.mcp_services.event_manager.models import (
    EventCreate, EventUpdate, EventResponse, EventSummary, 
    EventListResponse, EventAnalytics, EventStatus
)

# Using loguru logger imported above

class EventManagerService:
    """Service for managing events - focused on event owner operations"""
    
    def __init__(self):
        # In-memory storage (in production, use database)
        self.events: Dict[str, EventResponse] = {}  # event_id -> event data
        self.user_events: Dict[str, List[str]] = {}  # user_id -> list of event_ids they created
    
    def create_event(self, event_data: EventCreate) -> EventResponse:
        """Create a new event"""
        # Use provided event_id or generate a new UUID
        event_id = event_data.event_id if event_data.event_id else str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        event = EventResponse(
            event_id=event_id,
            title=event_data.title,
            description=event_data.description,
            location=event_data.location,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            status=EventStatus.DRAFT,
            created_by=event_data.created_by,
            max_capacity=event_data.max_capacity,
            require_approval=event_data.require_approval,
            created_at=now,
            updated_at=now,
            metadata=event_data.metadata
        )
        
        # Store event
        self.events[event_id] = event
        
        # Update user index
        if event_data.created_by not in self.user_events:
            self.user_events[event_data.created_by] = []
        self.user_events[event_data.created_by].append(event_id)
        
        logger.info(f"Created event {event_id}: {event_data.title} by {event_data.created_by}")
        return event
    
    def get_event(self, event_id: str) -> EventResponse:
        """Get event by ID"""
        if event_id not in self.events:
            raise ValueError(f"Event {event_id} not found")
        return self.events[event_id]
    
    def update_event(self, event_id: str, update_data: EventUpdate) -> EventResponse:
        """Update an existing event"""
        if event_id not in self.events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self.events[event_id]
        
        # Update fields if provided
        if update_data.title is not None:
            event.title = update_data.title
        if update_data.description is not None:
            event.description = update_data.description
        if update_data.location is not None:
            event.location = update_data.location
        if update_data.start_time is not None:
            event.start_time = update_data.start_time
        if update_data.end_time is not None:
            event.end_time = update_data.end_time
        if update_data.status is not None:
            event.status = update_data.status
        if update_data.max_capacity is not None:
            event.max_capacity = update_data.max_capacity
        if update_data.require_approval is not None:
            event.require_approval = update_data.require_approval
        if update_data.metadata is not None:
            event.metadata.update(update_data.metadata)
        
        event.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Updated event {event_id}")
        return event
    
    def delete_event(self, event_id: str) -> None:
        """Delete an event"""
        if event_id not in self.events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self.events[event_id]
        
        # Remove from user index
        if event.created_by in self.user_events:
            self.user_events[event.created_by].remove(event_id)
            if not self.user_events[event.created_by]:
                del self.user_events[event.created_by]
        
        # Remove event
        del self.events[event_id]
        
        logger.info(f"Deleted event {event_id}")
    
    def list_all_events(self, status: Optional[EventStatus] = None, limit: int = 100) -> EventListResponse:
        """List all events with optional status filter"""
        events = list(self.events.values())
        
        # Apply status filter if provided
        if status:
            events = [event for event in events if event.status == status]
        
        # Sort by creation date (newest first)
        events.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply limit
        events = events[:limit]
        
        # Convert to summaries
        summaries = [
            EventSummary(
                event_id=event.event_id,
                title=event.title,
                status=event.status,
                created_by=event.created_by,
                start_time=event.start_time,
                location=event.location,
                created_at=event.created_at
            )
            for event in events
        ]

        # Dump summaries to list of dicts for logging
        summary_dicts = [summary.model_dump() for summary in summaries]
        logger.info(f"List events: {summary_dicts}")

        return EventListResponse(
            events=summaries,
            total_count=len(summaries),
            filter_applied=status.value if status else None
        )
    
    def get_events_by_creator(self, creator_id: str) -> EventListResponse:
        """Get all events created by a specific user"""
        event_ids = self.user_events.get(creator_id, [])
        events = [self.events[event_id] for event_id in event_ids]
        
        # Sort by creation date (newest first)
        events.sort(key=lambda x: x.created_at, reverse=True)
        
        # Convert to summaries
        summaries = [
            EventSummary(
                event_id=event.event_id,
                title=event.title,
                status=event.status,
                created_by=event.created_by,
                start_time=event.start_time,
                location=event.location,
                created_at=event.created_at
            )
            for event in events
        ]
        
        return EventListResponse(
            events=summaries,
            total_count=len(summaries),
            filter_applied=f"creator:{creator_id}"
        )
    
    def get_events_by_status(self, status: EventStatus) -> EventListResponse:
        """Get all events with a specific status"""
        return self.list_all_events(status=status)
    
    def get_event_analytics(self, event_id: str) -> EventAnalytics:
        """Get analytics for an event (event-only data, no RSVP data)"""
        if event_id not in self.events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self.events[event_id]
        now = datetime.now(timezone.utc)
        
        # Calculate time-based metrics
        days_since_created = (now - event.created_at).days
        
        is_upcoming = False
        is_past_due = False
        
        if event.start_time:
            is_upcoming = event.start_time > now
            if event.end_time:
                is_past_due = event.end_time < now
            else:
                # If no end time, consider past due if start time has passed
                is_past_due = event.start_time < now
        
        # Capacity information
        capacity_info = None
        if event.max_capacity:
            capacity_info = {
                "max_capacity": event.max_capacity,
                "has_capacity_limit": True
            }
        else:
            capacity_info = {
                "max_capacity": None,
                "has_capacity_limit": False
            }
        
        return EventAnalytics(
            event_id=event.event_id,
            title=event.title,
            status=event.status,
            created_by=event.created_by,
            created_at=event.created_at,
            days_since_created=days_since_created,
            is_upcoming=is_upcoming,
            is_past_due=is_past_due,
            capacity_info=capacity_info,
            metadata=event.metadata
        )
    
    def get_event_stats(self) -> Dict[str, any]:
        """Get overall event statistics"""
        total_events = len(self.events)
        total_creators = len(self.user_events)
        
        # Count by status
        status_counts = {}
        for event in self.events.values():
            status_counts[event.status.value] = status_counts.get(event.status.value, 0) + 1
        
        # Count by creator
        events_per_creator = {}
        for creator_id, event_ids in self.user_events.items():
            events_per_creator[creator_id] = len(event_ids)
        
        # Find most active creator
        most_active_creator = max(events_per_creator.items(), key=lambda x: x[1])[0] if events_per_creator else None
        
        return {
            "total_events": total_events,
            "total_creators": total_creators,
            "status_breakdown": status_counts,
            "average_events_per_creator": total_events / max(1, total_creators),
            "most_active_creator": most_active_creator,
            "events_by_creator": events_per_creator
        }
    
    def search_events(self, query: str, limit: int = 50) -> EventListResponse:
        """Search events by title, description, or location"""
        query_lower = query.lower()
        matching_events = []
        
        for event in self.events.values():
            # Search in title, description, and location
            if (query_lower in event.title.lower() or
                (event.description and query_lower in event.description.lower()) or
                (event.location and query_lower in event.location.lower())):
                matching_events.append(event)
        
        # Sort by relevance (title matches first, then by creation date)
        def relevance_score(event):
            score = 0
            if query_lower in event.title.lower():
                score += 10
            if event.description and query_lower in event.description.lower():
                score += 5
            if event.location and query_lower in event.location.lower():
                score += 3
            return score
        
        matching_events.sort(key=lambda x: (relevance_score(x), x.created_at), reverse=True)
        matching_events = matching_events[:limit]
        
        # Convert to summaries
        summaries = [
            EventSummary(
                event_id=event.event_id,
                title=event.title,
                status=event.status,
                created_by=event.created_by,
                start_time=event.start_time,
                location=event.location,
                created_at=event.created_at
            )
            for event in matching_events
        ]
        
        return EventListResponse(
            events=summaries,
            total_count=len(summaries),
            filter_applied=f"search:{query}"
        )
    
    def save_event_to_guild_data(self, event_id: str, guild_id: str, event_data: Dict) -> Dict[str, any]:
        """Save event data to guild_data directory structure"""
        import os
        import json
        from pathlib import Path
        
        try:
            # Build path to event.json: guild_data/data/<guild_id>/<event_id>/event.json
            data_dir = Path(os.getenv('GUILD_DATA_DIR', './guild_data'))
            event_dir = data_dir / "data" / guild_id / event_id
            event_json_path = event_dir / "event.json"
            
            # Ensure directory exists
            event_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare event data with current timestamp
            event_save_data = {
                **event_data,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "event_id": event_id,
                "guild_id": guild_id
            }
            
            # Save to file
            with open(event_json_path, 'w') as f:
                json.dump(event_save_data, f, indent=2)
            
            logger.info(f"Event {event_id} saved to {event_json_path}")
            
            return {
                "success": True,
                "message": f"Event saved successfully to {event_json_path}",
                "file_path": str(event_json_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to save event {event_id} to guild_data: {e}")
            return {
                "success": False,
                "message": f"Failed to save event: {str(e)}",
                "error": str(e)
            }