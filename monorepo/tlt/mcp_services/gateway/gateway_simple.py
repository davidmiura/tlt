import os
import sys
import pprint
from loguru import logger
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import JSONResponse

# FastMCP Client imports
# # Note: Import order matters due to local 'mcp' directory shadowing the real mcp package
# _original_path = sys.path[:]
# # Temporarily remove paths that might cause mcp namespace collision
# for path in ['', '.', 'monorepo']:
#     if path in sys.path:
#         sys.path.remove(path)

# try:
from fastmcp import FastMCP
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
# finally:
#     # Restore original path
#     sys.path[:] = _original_path

from tlt.mcp_services.gateway.models import ProxyConfig, UserRole, AuthContext
from tlt.mcp_services.gateway.casbin_rbac import CasbinRBACMiddleware

# Using loguru logger imported above

class SimpleGateway:
    """Simplified MCP Gateway with HTTP forwarding and RBAC"""
    
    def __init__(self):
        self.mcp = FastMCP("TLT MCP Gateway")
        self.rbac = CasbinRBACMiddleware()

        @self.mcp.custom_route("/health", methods=["GET", "OPTIONS"])
        async def health_check(request: Request):
            return JSONResponse({"status": "healthy"})
        
        # Configure backend services
        self.backend_services = {
            'event_manager': {
                'name': 'Event Manager',
                'url': os.getenv('EVENT_MANAGER_URL', 'http://localhost:8004'),
                'tools': [
                    "create_event", "get_event", "update_event", "delete_event",
                    "list_all_events", "get_events_by_creator", "get_events_by_status",
                    "get_event_analytics", "search_events", "get_event_stats",
                    "save_event_to_guild_data"
                ]
            },
            'rsvp': {
                'name': 'RSVP Service', 
                'url': os.getenv('RSVP_URL', 'http://localhost:8007'),
                'tools': [
                    "create_rsvp", "get_rsvp", "update_rsvp", "delete_rsvp",
                    "get_user_rsvp_for_event", "get_event_rsvps", "get_user_rsvps",
                    "update_user_rsvp", "get_rsvp_analytics", "list_events_with_rsvps",
                    "get_rsvp_stats", "process_rsvp"
                ]
            },
            'guild_manager': {
                'name': 'Guild Manager',
                'url': os.getenv('GUILD_MANAGER_URL', 'http://localhost:8009'),
                'tools': [
                    "register_guild", "deregister_guild", "get_guild_info",
                    "list_guilds", "update_guild_settings", "get_guild_stats"
                ]
            },
            'photo_vibe_check': {
                'name': 'Photo Vibe Check',
                'url': os.getenv('PHOTO_VIBE_CHECK_URL', 'http://localhost:8005'),
                'tools': [
                    "submit_photo_dm", "activate_photo_collection", "deactivate_photo_collection",
                    "update_photo_settings", "add_pre_event_photos", "get_photo_status",
                    "get_event_photo_summary", "generate_event_slideshow", "get_user_photo_history"
                ]
            },
            'vibe_bit': {
                'name': 'Vibe Bit Canvas',
                'url': os.getenv('VIBE_BIT_URL', 'http://localhost:8006'),
                'tools': [
                    "vibe_bit", "create_vibe_canvas", "activate_vibe_canvas", "deactivate_vibe_canvas",
                    "update_vibe_settings", "get_vibe_canvas_image", "get_vibe_canvas_preview",
                    "get_vibe_canvas_stats", "get_user_vibe_history", "get_color_palettes",
                    "get_emoji_sets", "create_vibe_snapshot"
                ]
            }
        }
        
        self._setup_proxy_tools()
        self._setup_gateway_tools()
    
    def _check_permission(self, tool_name: str, **kwargs) -> Optional[AuthContext]:
        """Check RBAC permissions and return auth context"""
        # Allow bypass for development/testing when no auth context is provided
        if not kwargs or 'user_id' not in kwargs:
            logger.debug(f"No auth context provided for {tool_name}, allowing for development/testing")
            return None
            
        auth_context = self.rbac._extract_auth_context(kwargs)
        logger.info("AuthContext: {pprint.pformat(auth_context.model_dump())}")
        
        if not auth_context:
            logger.warning(f"No authentication context for tool {tool_name}, allowing for development")
            return None
        
        if not self.rbac.check_permission(tool_name, auth_context):
            logger.error(f"Access denied for user {auth_context.user_id} to tool {tool_name}")
            raise PermissionError(f"Access denied to tool '{tool_name}' for role '{auth_context.role.value}'")
        
        logger.debug(f"Access granted for {auth_context.user_id} ({auth_context.role.value}) to {tool_name}")
        return auth_context
    
    async def _forward_request(self, service_name: str, tool_name: str, **kwargs) -> Any:
        """Forward request to backend service using FastMCP Client"""
        service = self.backend_services[service_name]
        
        # Log every input MCP request as INFO for production visibility
        logger.info(f"MCP Request: service={service_name}, tool={tool_name}, args={kwargs}")
        
        # Extract auth context but don't forward it to backend services
        auth_context = kwargs.pop('auth_context', None)
        # auth_context is used for gateway-level authentication/authorization
        # but should not be forwarded to backend services
        
        # Log filtered arguments that will be forwarded
        logger.info(f"Forwarding to {service_name}: tool={tool_name}, filtered_args={kwargs}")
        
        try:
            # Create FastMCP Client with StreamableHttpTransport
            service_url = f"{service['url']}/mcp/"
            transport = StreamableHttpTransport(url=service_url)
            
            # Client info for MCP initialization
            client_info = {
                "name": "TLT-MCP-Gateway",
                "version": "2.0.0"
            }
            
            async with Client(transport, client_info=client_info) as client:
                # Call the tool using FastMCP Client
                result = await client.call_tool(
                    name=tool_name,
                    arguments=kwargs
                )
                
                # Log successful forwarding
                logger.info(f"Successfully forwarded to {service_name}, received result type: {type(result)}")
                
                # Extract result content based on FastMCP response format
                if hasattr(result, 'content') and result.content:
                    # Handle text content from tool response
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        try:
                            import json
                            # Try to parse as JSON first
                            parsed_result = json.loads(content.text)
                            logger.info(f"Successfully parsed JSON result from {service_name}")
                            return parsed_result
                        except (json.JSONDecodeError, AttributeError):
                            # If not JSON, return as string
                            logger.info(f"Returning text result from {service_name}")
                            return content.text
                    else:
                        logger.info(f"Returning string content from {service_name}")
                        return str(content)
                else:
                    # Fallback to direct result
                    logger.info(f"Returning direct result from {service_name}")
                    return result
                
        except Exception as e:
            logger.error(f"FastMCP Client error forwarding to {service_name}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Full error details: {repr(e)}")
            
            # Determine error type for better error messages
            error_msg = str(e)
            if "connect" in error_msg.lower() or "connection" in error_msg.lower():
                return {
                    "error": f"Service {service_name} is currently unavailable",
                    "service_name": service_name,
                    "tool_name": tool_name,
                    "available": False
                }
            elif "tool" in error_msg.lower() and "not found" in error_msg.lower():
                return {
                    "error": f"Tool '{tool_name}' not found in service {service_name}",
                    "service_name": service_name,
                    "tool_name": tool_name,
                    "available": True
                }
            else:
                return {
                    "error": f"Service {service_name} error: {error_msg}",
                    "service_name": service_name,
                    "tool_name": tool_name,
                    "available": False
                }
    
    def _setup_proxy_tools(self):
        """Set up proxy tools for all backend services"""
        
        # Event Manager Tools
        @self.mcp.tool()
        async def create_event(
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
            kwargs = {
                'title': title, 'created_by': created_by, 'guild_id': guild_id,
                'event_id': event_id, 'description': description, 'location': location,
                'start_time': start_time, 'end_time': end_time, 'max_capacity': max_capacity,
                'require_approval': require_approval,
                'metadata': metadata
            }
            auth_context = self._check_permission("create_event", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "create_event", **kwargs)
        
        @self.mcp.tool()
        async def get_event(event_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
            """Get event by ID.
            
            Args:
                event_id: ID of the event to retrieve
                user_id: Optional user ID for permission context
                
            Returns:
                Dict containing the event information
            """
            kwargs = {'event_id': event_id, 'user_id': user_id}
            auth_context = self._check_permission("get_event", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "get_event", **kwargs)
        
        @self.mcp.tool()
        async def update_event(
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
            kwargs = {
                'event_id': event_id, 'user_id': user_id, 'guild_id': guild_id,
                'title': title, 'description': description, 'location': location,
                'start_time': start_time, 'end_time': end_time, 'status': status,
                'max_capacity': max_capacity,
                'require_approval': require_approval, 'metadata': metadata
            }
            auth_context = self._check_permission("update_event", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "update_event", **kwargs)
        
        @self.mcp.tool()
        async def delete_event(event_id: str, user_id: str, guild_id: str) -> Dict[str, Any]:
            """Delete an event.
            
            Args:
                event_id: ID of the event to delete
                user_id: ID of the user deleting the event
                guild_id: Discord guild ID where the event exists
                
            Returns:
                Dict containing deletion confirmation
            """
            kwargs = {'event_id': event_id, 'user_id': user_id, 'guild_id': guild_id}
            auth_context = self._check_permission("delete_event", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "delete_event", **kwargs)
        
        @self.mcp.tool()
        async def list_all_events(
            status: Optional[str] = None,
            limit: int = 100
        ) -> Dict[str, Any]:
            """List all events with optional status filter.
            
            Args:
                status: Optional status filter (draft, scheduled, active, completed, cancelled)
                limit: Maximum number of events to return
                
            Returns:
                Dict containing list of events
            """
            kwargs = {'status': status, 'limit': limit}
            auth_context = self._check_permission("list_all_events", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "list_all_events", **kwargs)
        
        @self.mcp.tool()
        async def get_events_by_creator(creator_id: str) -> Dict[str, Any]:
            """Get all events created by a specific user.
            
            Args:
                creator_id: ID of the user who created the events
                
            Returns:
                Dict containing list of events created by the user
            """
            kwargs = {'creator_id': creator_id}
            auth_context = self._check_permission("get_events_by_creator", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "get_events_by_creator", **kwargs)
        
        @self.mcp.tool()
        async def get_events_by_status(status: str) -> Dict[str, Any]:
            """Get all events with a specific status.
            
            Args:
                status: Event status (draft, scheduled, active, completed, cancelled)
                
            Returns:
                Dict containing list of events with the specified status
            """
            kwargs = {'status': status}
            auth_context = self._check_permission("get_events_by_status", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "get_events_by_status", **kwargs)
        
        @self.mcp.tool()
        async def get_event_analytics(event_id: str) -> Dict[str, Any]:
            """Get analytics for an event (event-only data, no RSVP data).
            
            Args:
                event_id: ID of the event
                
            Returns:
                Dict containing event analytics
            """
            kwargs = {'event_id': event_id}
            auth_context = self._check_permission("get_event_analytics", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "get_event_analytics", **kwargs)
        
        @self.mcp.tool()
        async def search_events(
            query: str,
            limit: int = 50
        ) -> Dict[str, Any]:
            """Search events by title, description, or location.
            
            Args:
                query: Search query string
                limit: Maximum number of results to return
                
            Returns:
                Dict containing search results
            """
            kwargs = {'query': query, 'limit': limit}
            auth_context = self._check_permission("search_events", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "search_events", **kwargs)
        
        @self.mcp.tool()
        async def get_event_stats() -> Dict[str, Any]:
            """Get overall event statistics.
            
            Returns:
                Dict containing overall event statistics
            """
            kwargs = {}
            auth_context = self._check_permission("get_event_stats", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "get_event_stats", **kwargs)
        
        @self.mcp.tool()
        async def save_event_to_guild_data(
            event_id: str,
            guild_id: str,
            event_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Save event data to guild_data directory structure.
            
            Args:
                event_id: The message ID of the event (used as event identifier)
                guild_id: The Discord guild ID where the event was created
                event_data: Complete event data to save
                
            Returns:
                Dict containing save operation result
            """
            kwargs = {'event_id': event_id, 'guild_id': guild_id, 'event_data': event_data}
            auth_context = self._check_permission("save_event_to_guild_data", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("event_manager", "save_event_to_guild_data", **kwargs)
        
        # RSVP Tools (12 tools total)
        @self.mcp.tool()
        async def create_rsvp(
            guild_id: str,
            event_id: str,
            user_id: str,
            emoji: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Create a new RSVP.
            
            Args:
                guild_id: Discord guild ID for state management
                event_id: ID of the event
                user_id: ID of the user creating the RSVP
                emoji: Single emoji for RSVP response
                metadata: Optional additional RSVP data
                
            Returns:
                Dict containing the created RSVP information
            """
            kwargs = {
                'guild_id': guild_id, 'event_id': event_id, 'user_id': user_id, 'emoji': emoji,
                'metadata': metadata
            }
            auth_context = self._check_permission("create_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "create_rsvp", **kwargs)
        
        @self.mcp.tool()
        async def get_rsvp(guild_id: str, rsvp_id: str) -> Dict[str, Any]:
            """Get RSVP by ID.
            
            Args:
                guild_id: Discord guild ID for state management
                rsvp_id: ID of the RSVP to retrieve
                
            Returns:
                Dict containing the RSVP information
            """
            kwargs = {'guild_id': guild_id, 'rsvp_id': rsvp_id}
            auth_context = self._check_permission("get_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_rsvp", **kwargs)
        
        @self.mcp.tool()
        async def update_rsvp(
            guild_id: str,
            rsvp_id: str,
            emoji: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Update an existing RSVP.
            
            Args:
                guild_id: Discord guild ID for state management
                rsvp_id: ID of the RSVP to update
                emoji: New emoji for the RSVP
                metadata: Additional metadata to update
                
            Returns:
                Dict containing the updated RSVP information
            """
            kwargs = {
                'guild_id': guild_id, 'rsvp_id': rsvp_id, 'emoji': emoji, 'metadata': metadata
            }
            auth_context = self._check_permission("update_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "update_rsvp", **kwargs)
        
        @self.mcp.tool()
        async def delete_rsvp(guild_id: str, rsvp_id: str) -> Dict[str, Any]:
            """Delete an RSVP.
            
            Args:
                guild_id: Discord guild ID for state management
                rsvp_id: ID of the RSVP to delete
                
            Returns:
                Dict containing deletion confirmation
            """
            kwargs = {'guild_id': guild_id, 'rsvp_id': rsvp_id}
            auth_context = self._check_permission("delete_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "delete_rsvp", **kwargs)
        
        @self.mcp.tool()
        async def get_user_rsvp_for_event(
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
                Dict containing RSVP data or null with has_rsvp flag
            """
            kwargs = {'guild_id': guild_id, 'user_id': user_id, 'event_id': event_id}
            auth_context = self._check_permission("get_user_rsvp_for_event", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_user_rsvp_for_event", **kwargs)
        
        @self.mcp.tool()
        async def get_event_rsvps(guild_id: str, event_id: str) -> Dict[str, Any]:
            """Get all RSVPs for an event.
            
            Args:
                guild_id: Discord guild ID for state management
                event_id: ID of the event
                
            Returns:
                Dict containing EventRSVPSummary with emoji breakdown
            """
            kwargs = {'guild_id': guild_id, 'event_id': event_id}
            auth_context = self._check_permission("get_event_rsvps", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_event_rsvps", **kwargs)
        
        @self.mcp.tool()
        async def get_user_rsvps(guild_id: str, user_id: str) -> Dict[str, Any]:
            """Get all RSVPs for a user.
            
            Args:
                guild_id: Discord guild ID for state management
                user_id: ID of the user
                
            Returns:
                Dict containing UserRSVPSummary
            """
            kwargs = {'guild_id': guild_id, 'user_id': user_id}
            auth_context = self._check_permission("get_user_rsvps", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_user_rsvps", **kwargs)
        
        @self.mcp.tool()
        async def update_user_rsvp(
            guild_id: str,
            event_id: str,
            user_id: str,
            emoji: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Update or create RSVP for a user in an event (upsert operation).
            
            Args:
                guild_id: Discord guild ID for state management
                event_id: ID of the event
                user_id: ID of the user
                emoji: Emoji for the RSVP response
                metadata: Optional additional metadata
                
            Returns:
                Dict containing the RSVP information
            """
            kwargs = {
                'guild_id': guild_id, 'event_id': event_id, 'user_id': user_id, 'emoji': emoji, 'metadata': metadata
            }
            auth_context = self._check_permission("update_user_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "update_user_rsvp", **kwargs)
        
        @self.mcp.tool()
        async def get_rsvp_analytics(guild_id: str, event_id: str) -> Dict[str, Any]:
            """Get detailed analytics for an event's RSVPs.
            
            Args:
                guild_id: Discord guild ID for state management
                event_id: ID of the event
                
            Returns:
                Dict containing detailed RSVPAnalytics with timeline and breakdown
            """
            kwargs = {'guild_id': guild_id, 'event_id': event_id}
            auth_context = self._check_permission("get_rsvp_analytics", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_rsvp_analytics", **kwargs)
        
        @self.mcp.tool()
        async def list_events_with_rsvps(guild_id: str) -> Dict[str, Any]:
            """List all events that have RSVPs.
            
            Args:
                guild_id: Discord guild ID for state management
                
            Returns:
                Dict containing list of event IDs that have RSVPs
            """
            kwargs = {'guild_id': guild_id}
            auth_context = self._check_permission("list_events_with_rsvps", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "list_events_with_rsvps", **kwargs)
        
        @self.mcp.tool()
        async def get_rsvp_stats(guild_id: str) -> Dict[str, Any]:
            """Get overall RSVP statistics.
            
            Args:
                guild_id: Discord guild ID for state management
                
            Returns:
                Dict containing overall RSVP statistics
            """
            kwargs = {'guild_id': guild_id}
            auth_context = self._check_permission("get_rsvp_stats", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "get_rsvp_stats", **kwargs)
        
        @self.mcp.tool()
        async def process_rsvp(
            guild_id: str,
            event_id: str,
            user_id: str,
            rsvp_type: str,
            emoji: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Process RSVP with LLM scoring for attendance likelihood prediction.
            
            Args:
                guild_id: Discord guild ID for state management
                event_id: ID of the event
                user_id: ID of the user
                rsvp_type: Type of RSVP processing
                emoji: Emoji for the RSVP
                metadata: Optional additional metadata
                
            Returns:
                Dict containing RSVP data with LLM attendance scoring
            """
            kwargs = {
                'guild_id': guild_id, 'event_id': event_id, 'user_id': user_id, 'rsvp_type': rsvp_type,
                'emoji': emoji, 'metadata': metadata
            }
            auth_context = self._check_permission("process_rsvp", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("rsvp", "process_rsvp", **kwargs)
        
        # Guild Manager Tools (6 tools total - all async)
        @self.mcp.tool()
        async def register_guild(
            guild_id: str,
            guild_name: str,
            channel_id: str,
            channel_name: str,
            user_id: str,
            user_name: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Register a Discord guild for TLT events.
            
            Args:
                guild_id: Discord guild ID
                guild_name: Discord guild name
                channel_id: Discord channel ID for TLT events
                channel_name: Discord channel name
                user_id: User ID performing the registration
                user_name: User name performing the registration
                metadata: Optional additional guild registration data
                
            Returns:
                Dict containing guild registration confirmation
            """
            kwargs = {
                'guild_id': guild_id, 'guild_name': guild_name, 'channel_id': channel_id,
                'channel_name': channel_name, 'user_id': user_id, 'user_name': user_name,
                'metadata': metadata
            }
            auth_context = self._check_permission("register_guild", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "register_guild", **kwargs)
        
        @self.mcp.tool()
        async def deregister_guild(
            guild_id: str,
            guild_name: str,
            user_id: str,
            user_name: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Deregister a Discord guild from TLT events.
            
            Args:
                guild_id: Discord guild ID to deregister
                guild_name: Discord guild name
                user_id: User ID performing the deregistration
                user_name: User name performing the deregistration
                metadata: Optional additional deregistration data
                
            Returns:
                Dict containing guild deregistration confirmation
            """
            kwargs = {
                'guild_id': guild_id, 'guild_name': guild_name, 'user_id': user_id,
                'user_name': user_name, 'metadata': metadata
            }
            auth_context = self._check_permission("deregister_guild", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "deregister_guild", **kwargs)
        
        @self.mcp.tool()
        async def get_guild_info(guild_id: str) -> Dict[str, Any]:
            """Get information about a registered guild.
            
            Args:
                guild_id: Discord guild ID
                
            Returns:
                Dict containing guild information and configuration
            """
            kwargs = {'guild_id': guild_id}
            auth_context = self._check_permission("get_guild_info", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "get_guild_info", **kwargs)
        
        @self.mcp.tool()
        async def list_guilds(status: Optional[str] = None) -> Dict[str, Any]:
            """List all registered guilds with optional status filter.
            
            Args:
                status: Optional status filter for guilds
                
            Returns:
                Dict containing list of registered guilds
            """
            kwargs = {'status': status}
            auth_context = self._check_permission("list_guilds", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "list_guilds", **kwargs)
        
        @self.mcp.tool()
        async def update_guild_settings(
            guild_id: str,
            settings: Dict[str, Any],
            user_id: str
        ) -> Dict[str, Any]:
            """Update guild settings.
            
            Args:
                guild_id: Discord guild ID
                settings: New settings to apply
                user_id: User ID performing the update
                
            Returns:
                Dict containing updated guild settings
            """
            kwargs = {
                'guild_id': guild_id, 'settings': settings, 'user_id': user_id
            }
            auth_context = self._check_permission("update_guild_settings", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "update_guild_settings", **kwargs)
        
        @self.mcp.tool()
        async def get_guild_stats() -> Dict[str, Any]:
            """Get overall guild statistics.
            
            Returns:
                Dict containing guild statistics and analytics
            """
            kwargs = {}
            auth_context = self._check_permission("get_guild_stats", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("guild_manager", "get_guild_stats", **kwargs)
        
        # Photo Vibe Check Tools (10 tools total)
        @self.mcp.tool()
        async def submit_photo_dm(
            guild_id: str,
            event_id: str,
            user_id: str,
            photo_url: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Submit a photo for an event via DM.
            
            Args:
                guild_id: Discord guild ID (required)
                event_id: ID of the event
                user_id: ID of the user submitting the photo
                photo_url: URL of the photo to submit
                metadata: Optional additional photo metadata
                
            Returns:
                Dict containing submission result with rate_limit_remaining and next_allowed_submission
            """
            kwargs = {
                'guild_id': guild_id, 'event_id': event_id, 'user_id': user_id, 'photo_url': photo_url,
                'metadata': metadata
            }
            auth_context = self._check_permission("submit_photo_dm", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "submit_photo_dm", **kwargs)
        
        @self.mcp.tool()
        async def activate_photo_collection(
            event_id: str,
            admin_user_id: str,
            rate_limit_hours: int = 1,
            max_hours_after_event: int = 24,
            event_start_time: Optional[str] = None,
            pre_event_photos: Optional[List[str]] = None,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Activate photo collection for an event (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                rate_limit_hours: Hours between allowed photo submissions per user
                max_hours_after_event: Hours after event start to accept photos
                event_start_time: ISO timestamp of event start (optional)
                pre_event_photos: List of pre-event photo URLs
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing activation confirmation and configuration
            """
            kwargs = {
                'event_id': event_id, 'admin_user_id': admin_user_id,
                'rate_limit_hours': rate_limit_hours, 'max_hours_after_event': max_hours_after_event,
                'event_start_time': event_start_time, 'pre_event_photos': pre_event_photos
            }
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("activate_photo_collection", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "activate_photo_collection", **kwargs)
        
        @self.mcp.tool()
        async def deactivate_photo_collection(
            event_id: str,
            admin_user_id: str,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Deactivate photo collection for an event (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing deactivation confirmation
            """
            kwargs = {'event_id': event_id, 'admin_user_id': admin_user_id}
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("deactivate_photo_collection", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "deactivate_photo_collection", **kwargs)
        
        @self.mcp.tool()
        async def update_photo_settings(
            event_id: str,
            admin_user_id: str,
            rate_limit_hours: Optional[int] = None,
            max_hours_after_event: Optional[int] = None,
            event_start_time: Optional[str] = None,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Update photo collection settings (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                rate_limit_hours: New rate limit in hours
                max_hours_after_event: New max hours after event
                event_start_time: New event start time ISO string
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing updated photo settings
            """
            kwargs = {
                'event_id': event_id, 'admin_user_id': admin_user_id,
                'rate_limit_hours': rate_limit_hours, 'max_hours_after_event': max_hours_after_event,
                'event_start_time': event_start_time
            }
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("update_photo_settings", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "update_photo_settings", **kwargs)
        
        @self.mcp.tool()
        async def add_pre_event_photos(
            event_id: str,
            admin_user_id: str,
            photo_urls: List[str],
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Add pre-event photos (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                photo_urls: List of photo URLs to add
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing confirmation of added photos
            """
            kwargs = {
                'event_id': event_id, 'admin_user_id': admin_user_id, 'photo_urls': photo_urls
            }
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("add_pre_event_photos", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "add_pre_event_photos", **kwargs)
        
        @self.mcp.tool()
        async def get_photo_status(
            photo_id: str,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get photo processing status and analysis.
            
            Args:
                photo_id: ID of the photo
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing processing state, analysis scores, quality/relevance ratings
            """
            kwargs = {'photo_id': photo_id}
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("get_photo_status", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "get_photo_status", **kwargs)
        
        @self.mcp.tool()
        async def get_event_photo_summary(
            event_id: str,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get photo collection summary for an event.
            
            Args:
                event_id: ID of the event
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing status breakdown, time window info, config details
            """
            kwargs = {'event_id': event_id}
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("get_event_photo_summary", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "get_event_photo_summary", **kwargs)
        
        @self.mcp.tool()
        async def generate_event_slideshow(
            event_id: str,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Generate slideshow from approved event photos.
            
            Args:
                event_id: ID of the event
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing slideshow with approved photos and statistics
            """
            kwargs = {'event_id': event_id}
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("generate_event_slideshow", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "generate_event_slideshow", **kwargs)
        
        @self.mcp.tool()
        async def get_user_photo_history(
            user_id: str,
            event_id: Optional[str] = None,
            guild_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get photo submission history for a user.
            
            Args:
                user_id: ID of the user
                event_id: Optional event ID to filter by
                guild_id: Discord guild ID (optional)
                
            Returns:
                Dict containing user's photo submission history
            """
            kwargs = {'user_id': user_id, 'event_id': event_id}
            if guild_id is not None:
                kwargs['guild_id'] = guild_id
            auth_context = self._check_permission("get_user_photo_history", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("photo_vibe_check", "get_user_photo_history", **kwargs)
        
        # Vibe Bit Tools (15 tools total)
        @self.mcp.tool()
        async def vibe_bit(
            event_id: str,
            user_id: str,
            element_type: str,
            content: str,
            x: int,
            y: int,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Place an emoji or colored block on the event canvas.
            
            This is the main tool for vibe bit placement. Users can submit emojis or color blocks
            to be placed on a shared canvas.
            
            Args:
                event_id: ID of the event
                user_id: ID of the user placing the element
                element_type: Type of element ('emoji' or 'color_block')
                content: Emoji character or hex color code (e.g., '#FF0000')
                x: X coordinate on the canvas
                y: Y coordinate on the canvas
                metadata: Optional metadata (source info, etc.)
                
            Returns:
                Dict containing placement result and canvas position
            """
            kwargs = {
                'event_id': event_id, 'user_id': user_id, 'element_type': element_type,
                'content': content, 'x': x, 'y': y, 'metadata': metadata
            }
            auth_context = self._check_permission("vibe_bit", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "vibe_bit", **kwargs)
        
        @self.mcp.tool()
        async def create_vibe_canvas(
            event_id: str,
            admin_user_id: str,
            width: int = 256,
            height: int = 256,
            activated: bool = False,
            rate_limit_hours: int = 1,
            max_hours_after_event: int = 24,
            event_start_time: Optional[str] = None,
            background_color: str = "#FFFFFF",
            grid_size: int = 16,
            allow_overlap: bool = False
        ) -> Dict[str, Any]:
            """Create a vibe canvas for an event (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                width: Canvas width in pixels (32-1024)
                height: Canvas height in pixels (32-1024)
                activated: Whether the canvas is active for placements
                rate_limit_hours: Hours between allowed placements per user
                max_hours_after_event: Hours after event start to accept placements
                event_start_time: ISO timestamp of event start (optional)
                background_color: Hex color for canvas background
                grid_size: Size of placement grid cells in pixels
                allow_overlap: Whether elements can overlap at same position
                
            Returns:
                Dict containing canvas creation result
            """
            kwargs = {
                'event_id': event_id, 'admin_user_id': admin_user_id, 'width': width,
                'height': height, 'activated': activated, 'rate_limit_hours': rate_limit_hours,
                'max_hours_after_event': max_hours_after_event, 'event_start_time': event_start_time,
                'background_color': background_color, 'grid_size': grid_size, 'allow_overlap': allow_overlap
            }
            auth_context = self._check_permission("create_vibe_canvas", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "create_vibe_canvas", **kwargs)
        
        @self.mcp.tool()
        async def activate_vibe_canvas(
            event_id: str,
            admin_user_id: str
        ) -> Dict[str, Any]:
            """Activate vibe canvas for an event (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                
            Returns:
                Dict containing activation result
            """
            kwargs = {'event_id': event_id, 'admin_user_id': admin_user_id}
            auth_context = self._check_permission("activate_vibe_canvas", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "activate_vibe_canvas", **kwargs)
        
        @self.mcp.tool()
        async def deactivate_vibe_canvas(
            event_id: str,
            admin_user_id: str
        ) -> Dict[str, Any]:
            """Deactivate vibe canvas for an event (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                
            Returns:
                Dict containing deactivation result
            """
            kwargs = {'event_id': event_id, 'admin_user_id': admin_user_id}
            auth_context = self._check_permission("deactivate_vibe_canvas", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "deactivate_vibe_canvas", **kwargs)
        
        @self.mcp.tool()
        async def update_vibe_settings(
            event_id: str,
            admin_user_id: str,
            rate_limit_hours: Optional[int] = None,
            max_hours_after_event: Optional[int] = None,
            event_start_time: Optional[str] = None,
            background_color: Optional[str] = None,
            allow_overlap: Optional[bool] = None
        ) -> Dict[str, Any]:
            """Update vibe canvas settings (Admin only).
            
            Args:
                event_id: ID of the event
                admin_user_id: ID of the admin user
                rate_limit_hours: New rate limit in hours (optional)
                max_hours_after_event: New max hours after event (optional)
                event_start_time: New event start time ISO string (optional)
                background_color: New background color hex code (optional)
                allow_overlap: Whether to allow element overlap (optional)
                
            Returns:
                Dict containing update result
            """
            kwargs = {
                'event_id': event_id, 'admin_user_id': admin_user_id,
                'rate_limit_hours': rate_limit_hours, 'max_hours_after_event': max_hours_after_event,
                'event_start_time': event_start_time, 'background_color': background_color,
                'allow_overlap': allow_overlap
            }
            auth_context = self._check_permission("update_vibe_settings", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "update_vibe_settings", **kwargs)
        
        @self.mcp.tool()
        async def get_vibe_canvas_image(
            event_id: str,
            include_stats: bool = False,
            format: str = "base64"
        ) -> Dict[str, Any]:
            """Get the current vibe canvas as an image.
            
            Args:
                event_id: ID of the event
                include_stats: Whether to include statistics overlay
                format: Return format ('base64' or 'url')
                
            Returns:
                Dict containing canvas image data
            """
            kwargs = {
                'event_id': event_id, 'include_stats': include_stats, 'format': format
            }
            auth_context = self._check_permission("get_vibe_canvas_image", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_vibe_canvas_image", **kwargs)
        
        @self.mcp.tool()
        async def get_vibe_canvas_preview(
            event_id: str,
            max_size: int = 512
        ) -> Dict[str, Any]:
            """Get a smaller preview of the vibe canvas.
            
            Args:
                event_id: ID of the event
                max_size: Maximum dimension for the preview
                
            Returns:
                Dict containing preview image data
            """
            kwargs = {'event_id': event_id, 'max_size': max_size}
            auth_context = self._check_permission("get_vibe_canvas_preview", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_vibe_canvas_preview", **kwargs)
        
        @self.mcp.tool()
        async def get_vibe_canvas_stats(event_id: str) -> Dict[str, Any]:
            """Get statistics for the vibe canvas.
            
            Args:
                event_id: ID of the event
                
            Returns:
                Dict containing canvas statistics
            """
            kwargs = {'event_id': event_id}
            auth_context = self._check_permission("get_vibe_canvas_stats", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_vibe_canvas_stats", **kwargs)
        
        @self.mcp.tool()
        async def get_user_vibe_history(
            user_id: str,
            event_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get vibe placement history for a user.
            
            Args:
                user_id: ID of the user
                event_id: Optional event ID to filter by
                
            Returns:
                Dict containing user's placement history
            """
            kwargs = {'user_id': user_id, 'event_id': event_id}
            auth_context = self._check_permission("get_user_vibe_history", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_user_vibe_history", **kwargs)
        
        @self.mcp.tool()
        async def get_color_palettes() -> Dict[str, Any]:
            """Get available color palettes for vibe bit placement.
            
            Returns:
                Dict containing available color palettes
            """
            kwargs = {}
            auth_context = self._check_permission("get_color_palettes", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_color_palettes", **kwargs)
        
        @self.mcp.tool()
        async def get_emoji_sets() -> Dict[str, Any]:
            """Get available emoji sets for vibe bit placement.
            
            Returns:
                Dict containing available emoji sets
            """
            kwargs = {}
            auth_context = self._check_permission("get_emoji_sets", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "get_emoji_sets", **kwargs)
        
        @self.mcp.tool()
        async def create_vibe_snapshot(
            event_id: str,
            snapshot_type: str = "progress"
        ) -> Dict[str, Any]:
            """Create a snapshot of the current canvas state.
            
            Args:
                event_id: ID of the event
                snapshot_type: Type of snapshot ('progress' or 'final')
                
            Returns:
                Dict containing snapshot information
            """
            kwargs = {'event_id': event_id, 'snapshot_type': snapshot_type}
            auth_context = self._check_permission("create_vibe_snapshot", **kwargs)
            if auth_context:
                kwargs['auth_context'] = auth_context
            return await self._forward_request("vibe_bit", "create_vibe_snapshot", **kwargs)
        
        logger.info("Proxy tools configured for all backend services")
    
    def _setup_gateway_tools(self):
        """Set up gateway-specific management tools"""
        
        @self.mcp.tool()
        def ping() -> Dict[str, Any]:
            """Simple ping tool to test MCP connection"""
            return {
                "status": "pong",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "MCP Gateway is responding"
            }
        
        @self.mcp.tool()
        def get_gateway_status() -> Dict[str, Any]:
            """Get status of the MCP gateway and all backend services"""
            status = {
                "gateway": {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "2.0.0"
                },
                "backend_services": {}
            }
            
            for service_name, service in self.backend_services.items():
                status["backend_services"][service_name] = {
                    "name": service["name"],
                    "url": service["url"],
                    "tools_count": len(service["tools"])
                }
            
            return status
        
        @self.mcp.tool()
        def get_user_permissions(
            user_id: str,
            role: str = "user",
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Get list of tools and permissions for a user"""
            try:
                user_role = UserRole(role.lower())
                auth_context = AuthContext(
                    user_id=user_id,
                    role=user_role,
                    event_permissions=metadata.get('event_permissions', []) if metadata else [],
                    metadata=metadata or {}
                )
                
                allowed_tools = self.rbac.get_allowed_tools(auth_context)
                
                return {
                    "user_id": user_id,
                    "role": user_role.value,
                    "allowed_tool_patterns": allowed_tools,
                    "available_services": list(self.backend_services.keys())
                }
                
            except ValueError as e:
                return {
                    "error": f"Invalid role: {role}. Valid roles: {[r.value for r in UserRole]}"
                }
        
        @self.mcp.tool()
        def get_available_tools() -> Dict[str, Any]:
            """Get all available tools from backend services"""
            all_tools = {}
            
            for service_name, service in self.backend_services.items():
                all_tools[service_name] = {
                    "service_name": service["name"],
                    "url": service["url"],
                    "tools": service["tools"]
                }
            
            # Add gateway tools
            all_tools["gateway"] = {
                "service_name": "Gateway Management",
                "url": "local",
                "tools": [
                    "ping",
                    "get_gateway_status",
                    "get_user_permissions", 
                    "get_available_tools",
                    "get_casbin_policies",
                    "add_casbin_policy",
                    "remove_casbin_policy",
                    "get_user_roles",
                    "add_user_role",
                    "remove_user_role"
                ]
            }
            
            return all_tools
        
        @self.mcp.tool()
        def get_casbin_policies() -> Dict[str, Any]:
            """Get all Casbin RBAC policies"""
            try:
                policies = self.rbac.get_policy()
                return {
                    "policies": policies,
                    "total_policies": len(policies),
                    "roles": ["admin", "event_owner", "user"]
                }
            except Exception as e:
                return {"error": f"Failed to get policies: {str(e)}"}
        
        @self.mcp.tool()
        def add_casbin_policy(
            role: str,
            resource: str, 
            action: str,
            user_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Add a new Casbin RBAC policy"""
            try:
                # Check if user has admin privileges
                if user_id:
                    auth_context = AuthContext(user_id=user_id, role=UserRole.ADMIN, event_permissions=[], metadata={})
                    if not self.rbac.check_permission("add_casbin_policy", auth_context):
                        return {"error": "Access denied: Admin role required"}
                
                success = self.rbac.add_policy(role, resource, action)
                if success:
                    self.rbac.save_policy()
                    return {
                        "success": True,
                        "message": f"Added policy: {role} can {action} on {resource}"
                    }
                else:
                    return {"error": "Failed to add policy"}
            except Exception as e:
                return {"error": f"Failed to add policy: {str(e)}"}
        
        @self.mcp.tool()
        def remove_casbin_policy(
            role: str,
            resource: str,
            action: str,
            user_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Remove a Casbin RBAC policy"""
            try:
                # Check if user has admin privileges
                if user_id:
                    auth_context = AuthContext(user_id=user_id, role=UserRole.ADMIN, event_permissions=[], metadata={})
                    if not self.rbac.check_permission("remove_casbin_policy", auth_context):
                        return {"error": "Access denied: Admin role required"}
                
                success = self.rbac.remove_policy(role, resource, action)
                if success:
                    self.rbac.save_policy()
                    return {
                        "success": True,
                        "message": f"Removed policy: {role} can {action} on {resource}"
                    }
                else:
                    return {"error": "Policy not found or failed to remove"}
            except Exception as e:
                return {"error": f"Failed to remove policy: {str(e)}"}
        
        @self.mcp.tool()
        def get_user_roles(user_id: str) -> Dict[str, Any]:
            """Get all roles for a specific user"""
            try:
                roles = self.rbac.get_roles_for_user(user_id)
                permissions = []
                
                # Get permissions for each role
                for role in roles:
                    role_permissions = self.rbac.get_permissions_for_user(role)
                    permissions.extend(role_permissions)
                
                return {
                    "user_id": user_id,
                    "roles": roles,
                    "permissions": permissions,
                    "total_roles": len(roles),
                    "total_permissions": len(permissions)
                }
            except Exception as e:
                return {"error": f"Failed to get user roles: {str(e)}"}
        
        @self.mcp.tool()
        def add_user_role(
            user_id: str,
            role: str,
            admin_user_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Add a role to a user"""
            try:
                # Check if admin user has privileges
                if admin_user_id:
                    auth_context = AuthContext(user_id=admin_user_id, role=UserRole.ADMIN, event_permissions=[], metadata={})
                    if not self.rbac.check_permission("add_user_role", auth_context):
                        return {"error": "Access denied: Admin role required"}
                
                # Validate role
                try:
                    UserRole(role)
                except ValueError:
                    return {"error": f"Invalid role: {role}. Valid roles: {[r.value for r in UserRole]}"}
                
                success = self.rbac.add_role_for_user(user_id, role)
                if success:
                    self.rbac.save_policy()
                    return {
                        "success": True,
                        "message": f"Added role {role} to user {user_id}"
                    }
                else:
                    return {"error": "Failed to add role to user"}
            except Exception as e:
                return {"error": f"Failed to add user role: {str(e)}"}
        
        @self.mcp.tool()
        def remove_user_role(
            user_id: str,
            role: str,
            admin_user_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Remove a role from a user"""
            try:
                # Check if admin user has privileges
                if admin_user_id:
                    auth_context = AuthContext(user_id=admin_user_id, role=UserRole.ADMIN, event_permissions=[], metadata={})
                    if not self.rbac.check_permission("remove_user_role", auth_context):
                        return {"error": "Access denied: Admin role required"}
                
                success = self.rbac.delete_role_for_user(user_id, role)
                if success:
                    self.rbac.save_policy()
                    return {
                        "success": True,
                        "message": f"Removed role {role} from user {user_id}"
                    }
                else:
                    return {"error": "Role not found for user or failed to remove"}
            except Exception as e:
                return {"error": f"Failed to remove user role: {str(e)}"}
    
    def get_mcp_instance(self) -> FastMCP:
        """Get the configured FastMCP instance"""
        return self.mcp