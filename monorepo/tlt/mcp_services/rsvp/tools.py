import os
from typing import Dict, Any, Optional
from loguru import logger
from fastmcp import FastMCP
from datetime import datetime, timezone
from tlt.mcp_services.rsvp.service import RSVPService
from tlt.mcp_services.rsvp.models import (
    RSVPCreate, 
    RSVPUpdate,
    CreateRsvpResult,
    GetRsvpResult,
    UpdateRsvpResult,
    DeleteRsvpResult,
    GetUserRsvpForEventResult,
    GetEventRsvpsResult,
    GetUserRsvpsResult,
    UpdateUserRsvpResult,
    GetRsvpAnalyticsResult,
    ListEventsWithRsvpsResult,
    GetRsvpStatsResult,
    ProcessRsvpResult
)
from tlt.shared.user_state_manager import UserStateManager
from tlt.shared.event_state_manager import EventStateManager

# Using loguru logger imported above

def register_tools(mcp: FastMCP, rsvp_service: RSVPService):
    """Register all MCP tools for the RSVP service"""
    
    # Initialize state managers
    guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
    data_dir = os.path.join(guild_data_dir, 'data')
    user_state_manager = UserStateManager(data_dir)
    event_state_manager = EventStateManager(data_dir)
    
    @mcp.tool()
    def create_rsvp(
        guild_id: str,
        event_id: str,
        user_id: str, 
        emoji: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new RSVP for an event using a single emoji.
        
        Args:
            guild_id: Discord guild ID for state management
            event_id: ID of the event to RSVP to
            user_id: ID of the user creating the RSVP
            emoji: Single emoji representing the user's response
            metadata: Optional additional data
            
        Returns:
            Dict containing the created RSVP information
        """
        try:
            rsvp_data = RSVPCreate(
                event_id=event_id,
                user_id=user_id,
                emoji=emoji,
                metadata=metadata or {}
            )
            
            rsvp = rsvp_service.create_rsvp(rsvp_data)
            
            logger.info(f"RSVP created successfully: {rsvp.rsvp_id} for event {event_id} by {user_id} with emoji {emoji}")
            
            response = {
                "success": True,
                "rsvp": rsvp.model_dump(),
                "message": f"RSVP created successfully with emoji {emoji}"
            }
            
            # Save result to UserStateManager
            create_result = CreateRsvpResult(
                success=True,
                rsvp=rsvp.model_dump(),
                message=f"RSVP created successfully with emoji {emoji}",
                event_id=event_id,
                user_id=user_id,
                emoji=emoji,
                metadata=metadata
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, create_result)
            
            # Update event.json with RSVP data
            if guild_id:
                event_state_manager.append_to_array_field(guild_id, event_id, "rsvps", {
                    "rsvp_id": rsvp.rsvp_id,
                    "user_id": user_id,
                    "emoji": emoji,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": metadata or {}
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating RSVP: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id
                create_result = CreateRsvpResult(
                    success=False,
                    message="Failed to create RSVP",
                    error=str(e),
                    event_id=event_id,
                    user_id=user_id,
                    emoji=emoji,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, create_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_rsvp(
        guild_id: str,
        rsvp_id: str
    ) -> Dict[str, Any]:
        """Get RSVP by ID.
        
        Args:
            rsvp_id: ID of the RSVP to retrieve
            guild_id: Discord guild ID for state management
            
        Returns:
            Dict containing the RSVP information
        """
        try:
            rsvp = rsvp_service.get_rsvp(rsvp_id)
            
            logger.info(f"RSVP retrieved successfully: {rsvp_id} for event {rsvp.event_id} by {rsvp.user_id}")
            
            response = {
                "success": True,
                "rsvp": rsvp.model_dump()
            }
            
            # Save result to UserStateManager
            get_result = GetRsvpResult(
                success=True,
                rsvp=rsvp.model_dump(),
                rsvp_id=rsvp_id
            )
            user_state_manager.add_model_entry(guild_id, rsvp.event_id, rsvp.user_id, get_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting RSVP {rsvp_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                get_result = GetRsvpResult(
                    success=False,
                    error=str(e),
                    rsvp_id=rsvp_id
                )
                user_state_manager.add_model_entry(guild_id, "unknown", "system", get_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def update_rsvp(
        guild_id: str,
        rsvp_id: str,
        emoji: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing RSVP.
        
        Args:
            rsvp_id: ID of the RSVP to update
            emoji: New emoji for the RSVP
            metadata: Additional metadata to update
            guild_id: Discord guild ID for state management
            
        Returns:
            Dict containing the updated RSVP information
        """
        try:
            update_data = RSVPUpdate(
                emoji=emoji,
                metadata=metadata
            )
            
            rsvp = rsvp_service.update_rsvp(rsvp_id, update_data)
            
            logger.info(f"RSVP updated successfully: {rsvp_id} for event {rsvp.event_id} by {rsvp.user_id}")
            
            response = {
                "success": True,
                "rsvp": rsvp.model_dump(),
                "message": f"RSVP updated successfully"
            }
            
            # Save result to UserStateManager
            update_result = UpdateRsvpResult(
                success=True,
                rsvp=rsvp.model_dump(),
                message="RSVP updated successfully",
                rsvp_id=rsvp_id,
                emoji=emoji,
                metadata=metadata
            )
            user_state_manager.add_model_entry(guild_id, rsvp.event_id, rsvp.user_id, update_result)
            
            # Update event.json
            if guild_id:
                event_state_manager.update_nested_field(guild_id, rsvp.event_id, f"rsvps.{rsvp_id}.updated_at", datetime.now(timezone.utc).isoformat())
                if emoji:
                    event_state_manager.update_nested_field(guild_id, rsvp.event_id, f"rsvps.{rsvp_id}.emoji", emoji)
            
            return response
            
        except Exception as e:
            logger.error(f"Error updating RSVP {rsvp_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                update_result = UpdateRsvpResult(
                    success=False,
                    message="Failed to update RSVP",
                    error=str(e),
                    rsvp_id=rsvp_id,
                    emoji=emoji,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, "unknown", "system", update_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def delete_rsvp(
        guild_id: str,
        rsvp_id: str
    ) -> Dict[str, Any]:
        """Delete an RSVP.
        
        Args:
            rsvp_id: ID of the RSVP to delete
            guild_id: Discord guild ID for state management
            
        Returns:
            Dict containing deletion confirmation
        """
        try:
            # Get RSVP info before deletion for state management
            rsvp = rsvp_service.get_rsvp(rsvp_id)
            event_id = rsvp.event_id
            user_id = rsvp.user_id
            
            rsvp_service.delete_rsvp(rsvp_id)
            
            logger.info(f"RSVP deleted successfully: {rsvp_id}")
            
            response = {
                "success": True,
                "message": f"RSVP {rsvp_id} deleted successfully"
            }
            
            # Save result to UserStateManager
            delete_result = DeleteRsvpResult(
                success=True,
                message=f"RSVP {rsvp_id} deleted successfully",
                rsvp_id=rsvp_id
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, delete_result)
            
            # Update event.json
            if guild_id:
                event_state_manager.remove_from_array_field(guild_id, event_id, "rsvps", {"rsvp_id": rsvp_id})
            
            return response
            
        except Exception as e:
            logger.error(f"Error deleting RSVP {rsvp_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                delete_result = DeleteRsvpResult(
                    success=False,
                    message="Failed to delete RSVP",
                    error=str(e),
                    rsvp_id=rsvp_id
                )
                user_state_manager.add_model_entry(guild_id, "unknown", "system", delete_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_user_rsvp_for_event(
        guild_id: str,
        user_id: str,
        event_id: str
    ) -> Dict[str, Any]:
        """Get a user's RSVP for a specific event.
        
        Args:
            guild_id: Discord guild ID for state management
            user_id: ID of the user
            event_id: ID of the event
            
        Returns:
            Dict containing the user's RSVP for the event if it exists
        """
        try:
            rsvp = rsvp_service.get_user_rsvp_for_event(user_id, event_id)
            
            if rsvp:
                logger.info(f"User RSVP found for event: {event_id} by {user_id} - {rsvp.emoji}")
                response = {
                    "success": True,
                    "rsvp": rsvp.model_dump(),
                    "has_rsvp": True
                }
            else:
                logger.info(f"No RSVP found for user {user_id} in event {event_id}")
                response = {
                    "success": True,
                    "rsvp": None,
                    "has_rsvp": False,
                    "message": f"No RSVP found for user {user_id} in event {event_id}"
                }
            
            # Save result to UserStateManager
            user_rsvp_result = GetUserRsvpForEventResult(
                success=True,
                rsvp=rsvp.model_dump() if rsvp else None,
                has_rsvp=bool(rsvp),
                message=response.get("message"),
                user_id=user_id,
                event_id=event_id
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, user_rsvp_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting user RSVP: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                user_rsvp_result = GetUserRsvpForEventResult(
                    success=False,
                    has_rsvp=False,
                    error=str(e),
                    user_id=user_id,
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, user_rsvp_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_event_rsvps(
        guild_id: str,
        event_id: str
    ) -> Dict[str, Any]:
        """Get all RSVPs for an event.
        
        Args:
            guild_id: Discord guild ID for state management
            event_id: ID of the event
            
        Returns:
            Dict containing event RSVP summary and list of RSVPs
        """
        try:
            summary = rsvp_service.get_event_rsvps(event_id)
            
            logger.info(f"Event RSVPs retrieved: {event_id} - {len(summary.rsvps)} RSVPs")
            
            response = {
                "success": True,
                "summary": summary.model_dump()
            }
            
            # Save result to UserStateManager
            event_rsvps_result = GetEventRsvpsResult(
                success=True,
                summary=summary.model_dump(),
                event_id=event_id
            )
            user_state_manager.add_model_entry(guild_id, event_id, "system", event_rsvps_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting event RSVPs for {event_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                event_rsvps_result = GetEventRsvpsResult(
                    success=False,
                    error=str(e),
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id, event_id, "system", event_rsvps_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_user_rsvps(
        guild_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get all RSVPs for a user.
        
        Args:
            guild_id: Discord guild ID for state management
            user_id: ID of the user
            
        Returns:
            Dict containing user RSVP summary
        """
        try:
            summary = rsvp_service.get_user_rsvps(user_id)
            
            logger.info(f"User RSVPs retrieved: {user_id} - {len(summary.rsvps)} RSVPs")
            
            response = {
                "success": True,
                "summary": summary.model_dump()
            }
            
            # Save result to UserStateManager
            user_rsvps_result = GetUserRsvpsResult(
                success=True,
                summary=summary.model_dump(),
                user_id=user_id
            )
            user_state_manager.add_model_entry(guild_id, "all_events", user_id, user_rsvps_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting user RSVPs for {user_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                user_rsvps_result = GetUserRsvpsResult(
                    success=False,
                    error=str(e),
                    user_id=user_id
                )
                user_state_manager.add_model_entry(guild_id, "all_events", user_id, user_rsvps_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def update_user_rsvp(
        guild_id: str,
        event_id: str,
        user_id: str,
        emoji: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update or create RSVP for a user in an event.
        
        Args:
            guild_id: Discord guild ID for state management
            event_id: ID of the event
            user_id: ID of the user
            emoji: Single emoji for the RSVP
            metadata: Optional additional metadata
            
        Returns:
            Dict containing the updated/created RSVP
        """
        try:
            rsvp = rsvp_service.update_user_rsvp(event_id, user_id, emoji, metadata or {})
            
            logger.info(f"User RSVP updated successfully: {event_id} by {user_id} with emoji {emoji}")
            
            response = {
                "success": True,
                "rsvp": rsvp.model_dump(),
                "message": f"RSVP updated successfully with emoji {emoji}"
            }
            
            # Save result to UserStateManager
            update_user_rsvp_result = UpdateUserRsvpResult(
                success=True,
                rsvp=rsvp.model_dump(),
                message=f"RSVP updated successfully with emoji {emoji}",
                event_id=event_id,
                user_id=user_id,
                emoji=emoji,
                metadata=metadata
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, update_user_rsvp_result)
            
            # Update event.json with RSVP data
            event_state_manager.append_to_array_field(guild_id, event_id, "rsvp_updates", {
                "rsvp_id": rsvp.rsvp_id,
                "user_id": user_id,
                "emoji": emoji,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error updating user RSVP: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                update_user_rsvp_result = UpdateUserRsvpResult(
                    success=False,
                    message="Failed to update user RSVP",
                    error=str(e),
                    event_id=event_id,
                    user_id=user_id,
                    emoji=emoji,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, update_user_rsvp_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_rsvp_analytics(
        guild_id: str,
        event_id: str
    ) -> Dict[str, Any]:
        """Get detailed RSVP analytics for an event.
        
        Args:
            guild_id: Discord guild ID for state management
            event_id: ID of the event
            
        Returns:
            Dict containing detailed RSVP analytics
        """
        try:
            analytics = rsvp_service.get_rsvp_analytics(event_id)
            
            logger.info(f"RSVP analytics retrieved: {event_id} - {analytics.total_responses} total RSVPs")
            
            response = {
                "success": True,
                "analytics": analytics.model_dump()
            }
            
            # Save result to UserStateManager
            analytics_result = GetRsvpAnalyticsResult(
                success=True,
                analytics=analytics.model_dump(),
                event_id=event_id
            )
            user_state_manager.add_model_entry(guild_id, event_id, "system", analytics_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting RSVP analytics for {event_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                analytics_result = GetRsvpAnalyticsResult(
                    success=False,
                    error=str(e),
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id, event_id, "system", analytics_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def list_events_with_rsvps(
        guild_id: str
    ) -> Dict[str, Any]:
        """List all events that have RSVPs.
        
        Args:
            guild_id: Discord guild ID for state management
        
        Returns:
            Dict containing list of event IDs with RSVPs
        """
        try:
            events = rsvp_service.list_events_with_rsvps()
            
            logger.info(f"Events with RSVPs listed: {len(events)} events")
            
            response = {
                "success": True,
                "events": events,
                "count": len(events)
            }
            
            # Save result to UserStateManager
            list_events_result = ListEventsWithRsvpsResult(
                success=True,
                events=events,
                count=len(events)
            )
            user_state_manager.add_model_entry(guild_id, "global", "system", list_events_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error listing events with RSVPs: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                list_events_result = ListEventsWithRsvpsResult(
                    success=False,
                    error=str(e)
                )
                user_state_manager.add_model_entry(guild_id, "global", "system", list_events_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_rsvp_stats(
        guild_id: str
    ) -> Dict[str, Any]:
        """Get overall RSVP statistics.
        
        Args:
            guild_id: Discord guild ID for state management
        
        Returns:
            Dict containing overall RSVP statistics
        """
        try:
            stats = rsvp_service.get_rsvp_stats()
            
            logger.info(f"RSVP stats retrieved: {stats.get('total_rsvps', 0)} total RSVPs across {stats.get('total_events', 0)} events")
            
            response = {
                "success": True,
                "stats": stats
            }
            
            # Save result to UserStateManager
            stats_result = GetRsvpStatsResult(
                success=True,
                stats=stats
            )
            user_state_manager.add_model_entry(guild_id, "global", "system", stats_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting RSVP stats: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                stats_result = GetRsvpStatsResult(
                    success=False,
                    error=str(e)
                )
                user_state_manager.add_model_entry(guild_id, "global", "system", stats_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def process_rsvp(
        guild_id: str,
        event_id: str,
        user_id: str,
        rsvp_type: str,
        emoji: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process an RSVP reaction with LLM scoring to determine attendance likelihood.
        
        Args:
            guild_id: Discord guild ID for state management
            event_id: ID of the event
            user_id: ID of the user
            rsvp_type: Type of RSVP action (add/remove)
            emoji: The emoji used for the RSVP
            metadata: Optional additional metadata
            
        Returns:
            Dict containing RSVP processing result with LLM analysis
        """
        try:
            result = rsvp_service.process_rsvp_with_llm(
                event_id=event_id,
                user_id=user_id,
                rsvp_type=rsvp_type,
                emoji=emoji,
                metadata=metadata or {}
            )
            
            logger.info(f"RSVP processed with LLM scoring: {event_id} by {user_id} with emoji {emoji} - score: {result.get('attendance_score', 'N/A')} - confidence: {result.get('confidence', 'N/A')}")
            
            response = {
                "success": True,
                "result": result,
                "message": f"RSVP processed with LLM scoring for emoji {emoji}"
            }
            
            # Save result to UserStateManager
            process_result = ProcessRsvpResult(
                success=True,
                result=result,
                message=f"RSVP processed with LLM scoring for emoji {emoji}",
                event_id=event_id,
                user_id=user_id,
                rsvp_type=rsvp_type,
                emoji=emoji,
                metadata=metadata
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, process_result)
            
            # Update event.json with processed RSVP data
            event_state_manager.append_to_array_field(guild_id, event_id, "processed_rsvps", {
                "user_id": user_id,
                "rsvp_type": rsvp_type,
                "emoji": emoji,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "llm_result": result,
                "metadata": metadata or {}
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing RSVP with LLM: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                process_result = ProcessRsvpResult(
                    success=False,
                    message="Failed to process RSVP with LLM",
                    error=str(e),
                    event_id=event_id,
                    user_id=user_id,
                    rsvp_type=rsvp_type,
                    emoji=emoji,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, process_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response