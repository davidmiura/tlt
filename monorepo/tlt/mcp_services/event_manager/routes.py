from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from tlt.mcp_services.event_manager.models import RSVPCreate, RSVPUpdate, RSVPResponse, RSVPStatus, EventRSVPSummary, EventAnalytics
from tlt.mcp_services.event_manager.service import EventManagerService

def create_routes(event_manager: EventManagerService) -> APIRouter:
    router = APIRouter()

    # RSVP CRUD endpoints
    @router.post("/rsvp", response_model=RSVPResponse)
    async def create_rsvp(rsvp_data: RSVPCreate):
        """Create a new RSVP"""
        try:
            return event_manager.create_rsvp(rsvp_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/rsvp/{rsvp_id}", response_model=RSVPResponse)
    async def get_rsvp(rsvp_id: str):
        """Get RSVP by ID"""
        try:
            return event_manager.get_rsvp(rsvp_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.put("/rsvp/{rsvp_id}", response_model=RSVPResponse)
    async def update_rsvp(rsvp_id: str, update_data: RSVPUpdate):
        """Update an existing RSVP"""
        try:
            return event_manager.update_rsvp(rsvp_id, update_data)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.delete("/rsvp/{rsvp_id}")
    async def delete_rsvp(rsvp_id: str):
        """Delete an RSVP"""
        try:
            event_manager.delete_rsvp(rsvp_id)
            return {"status": "success", "message": f"RSVP {rsvp_id} deleted"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # Event-specific endpoints
    @router.get("/event/{event_id}/rsvps", response_model=EventRSVPSummary)
    async def get_event_rsvps(event_id: str):
        """Get all RSVPs for an event"""
        return event_manager.get_event_rsvps(event_id)

    @router.post("/event/{event_id}/rsvp", response_model=RSVPResponse)
    async def update_user_rsvp(
        event_id: str,
        user_id: str,
        status: RSVPStatus,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update or create RSVP for a user in an event"""
        return event_manager.update_user_rsvp(event_id, user_id, status, metadata or {})

    @router.get("/analytics/{event_id}", response_model=EventAnalytics)
    async def get_event_analytics(event_id: str):
        """Get detailed analytics for an event"""
        return event_manager.get_event_analytics(event_id)

    # Utility endpoints
    @router.get("/events")
    async def list_events():
        """List all events that have RSVPs"""
        return event_manager.list_events()

    @router.get("/user/{user_id}/rsvps")
    async def get_user_rsvps(user_id: str):
        """Get all RSVPs for a user"""
        return event_manager.get_user_rsvps(user_id)

    @router.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "total_rsvps": len(event_manager.rsvps),
            "total_events": len(event_manager.event_rsvps)
        }

    # MCP Protocol support
    @router.post("/query")
    async def handle_query(query_data: Dict[str, Any]):
        """Handle MCP agent queries"""
        query = query_data.get("query", "").lower()
        metadata = query_data.get("metadata", {})
        
        # Simple query processing
        if "attendance" in query or "who's attending" in query:
            event_id = metadata.get("event_id")
            if event_id:
                summary = event_manager.get_event_rsvps(event_id)
                return {
                    "response": f"Event {event_id} has {summary.attending_count} attendees, {summary.maybe_count} maybes, and {summary.not_attending_count} not attending.",
                    "data": summary.dict()
                }
        
        if "analytics" in query or "statistics" in query:
            event_id = metadata.get("event_id")
            if event_id:
                analytics = event_manager.get_event_analytics(event_id)
                return {
                    "response": f"Event {event_id} has {analytics.total_responses} total responses.",
                    "data": analytics.dict()
                }
        
        return {
            "response": "I can help with RSVP management and event analytics. Try asking about attendance or analytics for a specific event.",
            "capabilities": [
                "RSVP creation and management",
                "Event attendance tracking", 
                "RSVP analytics and reporting",
                "User RSVP history"
            ]
        }

    return router