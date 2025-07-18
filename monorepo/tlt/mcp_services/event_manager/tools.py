from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.event_manager.service import EventManagerService
from tlt.mcp_services.event_manager.models import (
    EventStatus, EventCreate, EventUpdate,
    CreateEventResult, GetEventResult, UpdateEventResult, DeleteEventResult,
    ListAllEventsResult, GetEventsByCreatorResult, GetEventsByStatusResult,
    GetEventAnalyticsResult, SearchEventsResult, GetEventStatsResult,
    SaveEventToGuildDataResult
)
from tlt.shared.user_state_manager import UserStateManager
from tlt.shared.event_state_manager import EventStateManager
import os

# Using loguru logger imported above

def register_tools(mcp: FastMCP, event_manager: EventManagerService):
    """Register all MCP tools for the event manager (event owner operations only)"""
    
    # Initialize state managers
    guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
    data_dir = os.path.join(guild_data_dir, 'data')
    user_state_manager = UserStateManager(data_dir)
    event_state_manager = EventStateManager(data_dir)
    
    @mcp.tool()
    def create_event(
        title: str,
        created_by: str,
        guild_id: str,
        event_id: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_capacity: Optional[int] = None,
        require_approval: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new event.
        
        Args:
            title: Event title
            created_by: ID of the user creating the event
            guild_id: Discord guild ID where the event is created
            event_id: Optional event ID to use (if not provided, a UUID will be generated)
            description: Optional event description
            location: Optional event location
            start_time: Optional event start time (ISO format)
            end_time: Optional event end time (ISO format)
            max_capacity: Optional maximum number of attendees
            require_approval: Whether RSVPs require approval
            metadata: Optional additional event data
            
        Returns:
            Dict containing the created event information
        """
        try:
            from datetime import datetime
            
            # Parse datetime strings if provided
            parsed_start_time = None
            parsed_end_time = None
            
            if start_time:
                try:
                    parsed_start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Invalid start_time format: {e}"
                    }
            
            if end_time:
                try:
                    parsed_end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Invalid end_time format: {e}"
                    }
            
            event_data = EventCreate(
                title=title,
                created_by=created_by,
                description=description,
                location=location,
                start_time=parsed_start_time,
                end_time=parsed_end_time,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata or {},
                event_id=event_id  # Pass the optional event_id
            )
            
            event = event_manager.create_event(event_data)
            
            # Save result to user state
            result = CreateEventResult(
                success=True,
                event_id=event.event_id,
                message=f"Event '{title}' created successfully",
                event=event.model_dump(),
                user_id=created_by,
                guild_id=guild_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event.event_id, created_by, result)
                
                # Update event.json with event data
                event_state_manager.update_event_field(guild_id, event.event_id, "event_manager_data", event.model_dump())
                event_state_manager.update_event_field(guild_id, event.event_id, "created_via_tool", True)
                
            except Exception as state_error:
                logger.warning(f"Failed to save create_event state: {state_error}")
            
            logger.info(f"Event created successfully: {event.event_id} - '{title}' by {created_by}")
            
            return {
                "id": event.event_id,
                "success": True,
                "event": event.model_dump(),
                "message": f"Event '{title}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            
            # Save error result to user state
            error_result = CreateEventResult(
                success=False,
                message=f"Failed to create event: {str(e)}",
                error=str(e),
                user_id=created_by,
                guild_id=guild_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata
            )
            
            try:
                # Use a temporary event_id for error cases
                temp_event_id = f"error_create_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, temp_event_id, created_by, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save create_event error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_event(event_id: str, guild_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            guild_id: Discord guild ID where the event exists
            user_id: Optional user ID for permission context
            
        Returns:
            Dict containing the event information
        """
        try:
            event = event_manager.get_event(event_id)
            
            # Save result to user state if user_id provided
            if user_id:
                result = GetEventResult(
                    success=True,
                    event=event.model_dump(),
                    event_id=event_id,
                    user_id=user_id,
                    guild_id=guild_id
                )
                
                try:
                    user_state_manager.add_model_entry(guild_id, event_id, user_id, result)
                except Exception as state_error:
                    logger.warning(f"Failed to save get_event state: {state_error}")
            
            logger.info(f"Event retrieved successfully: {event_id} - '{event.title}'")
            
            return {
                "success": True,
                "event": event.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error getting event {event_id}: {e}")
            
            # Save error result to user state if user_id provided
            if user_id:
                error_result = GetEventResult(
                    success=False,
                    error=str(e),
                    event_id=event_id,
                    user_id=user_id,
                    guild_id=guild_id
                )
                
                try:
                    user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
                except Exception as state_error:
                    logger.warning(f"Failed to save get_event error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def update_event(
        event_id: str,
        user_id: str,
        guild_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        status: Optional[str] = None,
        max_capacity: Optional[int] = None,
        require_approval: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update an existing event.
        
        Args:
            event_id: ID of the event to update
            user_id: ID of the user updating the event
            guild_id: Discord guild ID where the event exists
            title: New event title
            description: New event description
            location: New event location
            start_time: New event start time (ISO format)
            end_time: New event end time (ISO format)
            status: New event status (draft, scheduled, active, completed, cancelled)
            max_capacity: New maximum capacity
            require_approval: New approval requirement
            metadata: Additional metadata to update
            
        Returns:
            Dict containing the updated event information
        """
        try:
            from datetime import datetime
            
            # Parse datetime strings if provided
            parsed_start_time = None
            parsed_end_time = None
            
            if start_time:
                try:
                    parsed_start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Invalid start_time format: {e}"
                    }
            
            if end_time:
                try:
                    parsed_end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Invalid end_time format: {e}"
                    }
            
            # Parse status if provided
            parsed_status = None
            if status:
                try:
                    parsed_status = EventStatus(status.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid status: {status}. Valid statuses: {[s.value for s in EventStatus]}"
                    }
            
            update_data = EventUpdate(
                title=title,
                description=description,
                location=location,
                start_time=parsed_start_time,
                end_time=parsed_end_time,
                status=parsed_status,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata
            )
            
            event = event_manager.update_event(event_id, update_data)
            
            # Save result to user state
            result = UpdateEventResult(
                success=True,
                event=event.model_dump(),
                message=f"Event {event_id} updated successfully",
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                status=status,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, result)
                
                # Update event.json with updated event data
                event_state_manager.update_event_field(guild_id, event_id, "event_manager_data", event.model_dump())
                event_state_manager.update_event_field(guild_id, event_id, "last_updated_via_tool", datetime.now().isoformat())
                
            except Exception as state_error:
                logger.warning(f"Failed to save update_event state: {state_error}")
            
            logger.info(f"Event updated successfully: {event_id} - '{event.title}'")
            
            return {
                "success": True,
                "event": event.model_dump(),
                "message": f"Event {event_id} updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {e}")
            
            # Save error result to user state
            error_result = UpdateEventResult(
                success=False,
                message=f"Failed to update event: {str(e)}",
                error=str(e),
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                status=status,
                max_capacity=max_capacity,
                require_approval=require_approval,
                metadata=metadata
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save update_event error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def delete_event(event_id: str, user_id: str, guild_id: str) -> Dict[str, Any]:
        """Delete an event.
        
        Args:
            event_id: ID of the event to delete
            user_id: ID of the user deleting the event
            guild_id: Discord guild ID where the event exists
            
        Returns:
            Dict containing deletion confirmation
        """
        try:
            event_manager.delete_event(event_id)
            
            # Save result to user state
            result = DeleteEventResult(
                success=True,
                message=f"Event {event_id} deleted successfully",
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, result)
                
                # Update event.json to mark as deleted
                event_state_manager.update_event_field(guild_id, event_id, "deleted_via_tool", True)
                event_state_manager.update_event_field(guild_id, event_id, "deleted_at", datetime.now().isoformat())
                
            except Exception as state_error:
                logger.warning(f"Failed to save delete_event state: {state_error}")
            
            logger.info(f"Event deleted successfully: {event_id}")
            
            return {
                "success": True,
                "message": f"Event {event_id} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {e}")
            
            # Save error result to user state
            error_result = DeleteEventResult(
                success=False,
                message=f"Failed to delete event: {str(e)}",
                error=str(e),
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save delete_event error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def list_all_events(
        user_id: str,
        guild_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List all events with optional status filter.
        
        Args:
            user_id: ID of the user requesting the list
            guild_id: Discord guild ID to filter events
            status: Optional status filter (draft, scheduled, active, completed, cancelled)
            limit: Maximum number of events to return
            
        Returns:
            Dict containing list of events
        """
        try:
            # Parse status if provided
            parsed_status = None
            if status:
                try:
                    parsed_status = EventStatus(status.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid status: {status}. Valid statuses: {[s.value for s in EventStatus]}"
                    }
            
            result = event_manager.list_all_events(status=parsed_status, limit=limit)
            
            # Save result to user state
            state_result = ListAllEventsResult(
                success=True,
                result=result.model_dump(),
                user_id=user_id,
                guild_id=guild_id,
                status=status,
                limit=limit
            )
            
            try:
                # Use a generic event_id for list operations
                list_event_id = f"list_all_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, list_event_id, user_id, state_result)
            except Exception as state_error:
                logger.warning(f"Failed to save list_all_events state: {state_error}")
            
            logger.info(f"Events listed successfully: {len(result.events)} events (status: {status or 'all'}, limit: {limit})")
            
            return {
                "success": True,
                "result": result.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            
            # Save error result to user state
            error_result = ListAllEventsResult(
                success=False,
                error=str(e),
                user_id=user_id,
                guild_id=guild_id,
                status=status,
                limit=limit
            )
            
            try:
                list_event_id = f"list_all_error_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, list_event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save list_all_events error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_events_by_creator(creator_id: str, user_id: str, guild_id: str) -> Dict[str, Any]:
        """Get all events created by a specific user.
        
        Args:
            creator_id: ID of the user who created the events
            user_id: ID of the user requesting the data
            guild_id: Discord guild ID to filter events
            
        Returns:
            Dict containing list of events created by the user
        """
        try:
            result = event_manager.get_events_by_creator(creator_id)
            
            # Save result to user state
            state_result = GetEventsByCreatorResult(
                success=True,
                result=result.model_dump(),
                creator_id=creator_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                creator_event_id = f"creator_{creator_id}_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, creator_event_id, user_id, state_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_events_by_creator state: {state_error}")
            
            logger.info(f"Events retrieved by creator successfully: {creator_id} - {len(result.events)} events")
            
            return {
                "success": True,
                "result": result.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error getting events by creator {creator_id}: {e}")
            
            # Save error result to user state
            error_result = GetEventsByCreatorResult(
                success=False,
                error=str(e),
                creator_id=creator_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                creator_event_id = f"creator_error_{creator_id}_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, creator_event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_events_by_creator error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_events_by_status(status: str, user_id: str, guild_id: str) -> Dict[str, Any]:
        """Get all events with a specific status.
        
        Args:
            status: Event status (draft, scheduled, active, completed, cancelled)
            user_id: ID of the user requesting the data
            guild_id: Discord guild ID to filter events
            
        Returns:
            Dict containing list of events with the specified status
        """
        try:
            try:
                parsed_status = EventStatus(status.lower())
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid status: {status}. Valid statuses: {[s.value for s in EventStatus]}"
                }
            
            result = event_manager.get_events_by_status(parsed_status)
            
            # Save result to user state
            state_result = GetEventsByStatusResult(
                success=True,
                result=result.model_dump(),
                status=status,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                status_event_id = f"status_{status}_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, status_event_id, user_id, state_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_events_by_status state: {state_error}")
            
            logger.info(f"Events retrieved by status successfully: {status} - {len(result.events)} events")
            
            return {
                "success": True,
                "result": result.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error getting events by status {status}: {e}")
            
            # Save error result to user state
            error_result = GetEventsByStatusResult(
                success=False,
                error=str(e),
                status=status,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                status_event_id = f"status_error_{status}_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, status_event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_events_by_status error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_event_analytics(event_id: str, user_id: str, guild_id: str) -> Dict[str, Any]:
        """Get analytics for an event (event-only data, no RSVP data).
        
        Args:
            event_id: ID of the event
            user_id: ID of the user requesting analytics
            guild_id: Discord guild ID where the event exists
            
        Returns:
            Dict containing event analytics
        """
        try:
            analytics = event_manager.get_event_analytics(event_id)
            
            # Save result to user state
            result = GetEventAnalyticsResult(
                success=True,
                analytics=analytics.model_dump(),
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_event_analytics state: {state_error}")
            
            logger.info(f"Event analytics retrieved successfully: {event_id}")
            
            return {
                "success": True,
                "analytics": analytics.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error getting event analytics for {event_id}: {e}")
            
            # Save error result to user state
            error_result = GetEventAnalyticsResult(
                success=False,
                error=str(e),
                event_id=event_id,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_event_analytics error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def search_events(
        query: str,
        user_id: str,
        guild_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search events by title, description, or location.
        
        Args:
            query: Search query string
            user_id: ID of the user performing the search
            guild_id: Discord guild ID to filter events
            limit: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        try:
            result = event_manager.search_events(query, limit)
            
            # Save result to user state
            state_result = SearchEventsResult(
                success=True,
                result=result.model_dump(),
                query=query,
                user_id=user_id,
                guild_id=guild_id,
                limit=limit
            )
            
            try:
                search_event_id = f"search_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, search_event_id, user_id, state_result)
            except Exception as state_error:
                logger.warning(f"Failed to save search_events state: {state_error}")
            
            logger.info(f"Events searched successfully: query='{query}', {len(result.events)} results")
            
            return {
                "success": True,
                "result": result.model_dump(),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error searching events with query '{query}': {e}")
            
            # Save error result to user state
            error_result = SearchEventsResult(
                success=False,
                error=str(e),
                query=query,
                user_id=user_id,
                guild_id=guild_id,
                limit=limit
            )
            
            try:
                search_event_id = f"search_error_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, search_event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save search_events error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_event_stats(user_id: str, guild_id: str) -> Dict[str, Any]:
        """Get overall event statistics.
        
        Args:
            user_id: ID of the user requesting statistics
            guild_id: Discord guild ID to filter statistics
        
        Returns:
            Dict containing overall event statistics
        """
        try:
            stats = event_manager.get_event_stats()
            
            # Save result to user state
            result = GetEventStatsResult(
                success=True,
                stats=stats,
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                stats_event_id = f"stats_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, stats_event_id, user_id, result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_event_stats state: {state_error}")
            
            logger.info(f"Event stats retrieved successfully: {stats.get('total_events', 0)} total events")
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting event stats: {e}")
            
            # Save error result to user state
            error_result = GetEventStatsResult(
                success=False,
                error=str(e),
                user_id=user_id,
                guild_id=guild_id
            )
            
            try:
                stats_event_id = f"stats_error_{int(datetime.now().timestamp())}"
                user_state_manager.add_model_entry(guild_id, stats_event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save get_event_stats error state: {state_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def save_event_to_guild_data(
        event_id: str, 
        guild_id: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save event data to guild_data directory structure.
        
        This tool persists event state to guild_data/data/<guild_id>/<event_id>/event.json
        
        Args:
            event_id: The message ID of the event (used as event identifier)
            guild_id: The Discord guild ID where the event was created
            event_data: Complete event data to save
            user_id: ID of the user performing the save operation (optional, extracted from event_data if not provided)
            
        Returns:
            Dict containing save operation result
        """
        try:
            # Extract user_id from event_data if not provided
            if user_id is None:
                user_id = str(event_data.get('user_id', event_data.get('creator_id', 'system')))
            
            result = event_manager.save_event_to_guild_data(event_id, guild_id, event_data)
            
            # Save result to user state
            state_result = SaveEventToGuildDataResult(
                success=result["success"],
                message=result.get("message", ""),
                error=result.get("error"),
                event_id=event_id,
                guild_id=guild_id,
                user_id=user_id,
                event_data=event_data
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, state_result)
                
                # Also update the event.json with guild data save info
                if result["success"]:
                    event_state_manager.update_event_field(guild_id, event_id, "saved_to_guild_data", True)
                    event_state_manager.update_event_field(guild_id, event_id, "guild_data_saved_at", datetime.now().isoformat())
                
            except Exception as state_error:
                logger.warning(f"Failed to save save_event_to_guild_data state: {state_error}")
            
            if result["success"]:
                logger.info(f"Event {event_id} saved to guild_data for guild {guild_id}")
            else:
                logger.warning(f"Failed to save event {event_id} to guild_data: {result.get('message', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving event {event_id} to guild_data: {e}")
            
            # Extract user_id for error handling if not already set
            if user_id is None:
                user_id = str(event_data.get('user_id', event_data.get('creator_id', 'system')))
            
            # Save error result to user state
            error_result = SaveEventToGuildDataResult(
                success=False,
                message=f"Failed to save event to guild_data: {str(e)}",
                error=str(e),
                event_id=event_id,
                guild_id=guild_id,
                user_id=user_id,
                event_data=event_data
            )
            
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
            except Exception as state_error:
                logger.warning(f"Failed to save save_event_to_guild_data error state: {state_error}")
            
            return {
                "success": False,
                "message": f"Failed to save event to guild_data: {str(e)}",
                "error": str(e)
            }