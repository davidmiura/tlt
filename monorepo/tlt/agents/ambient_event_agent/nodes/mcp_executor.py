"""MCP tool execution node for ambient event agent"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from loguru import logger

# FastMCP Client imports  
# With mcp_services directory rename, namespace collision should be resolved
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from tlt.agents.ambient_event_agent.nodes.base import BaseNode
from tlt.agents.ambient_event_agent.state.state import (
    AgentState, AgentStatus, track_agent_task_lifecycle, 
    AgentTaskLifecycleStatus, get_agent_task_provenance, log_agent_task_provenance
)

class MCPExecutorNode(BaseNode):
    """Execute MCP tool calls through the gateway for ambient event agent
    
    Refactored to route ALL MCP calls through the gateway instead of direct service calls.
    
    This implementation:
    - Uses FastMCP Client with StreamableHttpTransport for MCP communication
    - Routes all tool calls through the MCP Gateway (port 8003)
    - Maps service-specific actions to gateway tool names
    - Handles async context management for client connections
    - Supports full MCP protocol with proper session management
    - Provides consistent error handling and logging
    
    Gateway routes to these backend services:
    - event_manager: Event Manager service (port 8004)
    - photo_vibe_check: Photo Vibe Check service (port 8005)
    - vibe_bit: Vibe Bit service (port 8006) 
    - rsvp: RSVP service (port 8007)
    - guild_manager: Guild Manager service (port 8009)
    """
    
    def __init__(self):
        super().__init__("mcp_executor")
        
        # Only use gateway for all MCP communication
        self.gateway_url = os.getenv('MCP_GATEWAY_URL', 'http://localhost:8003/mcp/')
        
        # All tool calls go through gateway
        self.service_name = "gateway"
        
        # Client info for MCP initialization
        self.client_info = {
            "name": "Ambient-Event-Agent", 
            "version": "1.0.0"
        }
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute pending MCP tool calls"""
        self.log_execution(state, "Executing MCP operations")
        
        # Log entry with detailed state info
        logger.info(f"MCPExecutor: Starting execution - pending_events={len(state.get('pending_events', []))}, pending_mcp_requests={len(state.get('pending_mcp_requests', []))}")
        
        try:
            self.update_state_metadata(state, {
                "status": AgentStatus.PROCESSING,
                "processing_step": "executing_mcp_calls"
            })
            
            # Execute any pending tool calls based on recent decisions
            await self._execute_tool_calls(state)
            
            # Update event context cache
            await self._refresh_event_cache(state)
            
            # Check service health
            await self._check_service_health(state)
            
            self.update_state_metadata(state, {
                "processing_step": "mcp_execution_complete"
            })
            
        except Exception as e:
            self.handle_error(state, e, "MCP execution")
            state["status"] = AgentStatus.ERROR
        
        return state
    
    
    
    async def _execute_tool_calls(self, state: AgentState):
        """Execute tool calls based on recent decisions and pending MCP requests"""
        
        # Execute pending MCP requests from reasoning node
        if "pending_mcp_requests" in state and state["pending_mcp_requests"]:
            logger.info(f"MCPExecutor: Processing {len(state['pending_mcp_requests'])} pending MCP requests")
            for i, request in enumerate(state["pending_mcp_requests"]):
                logger.info(f"MCPExecutor: Processing request {i+1}/{len(state['pending_mcp_requests'])}: {request}")
                
                # Track AgentTask entering MCP executor
                associated_task_id = request.get("metadata", {}).get("associated_task_id")
                if associated_task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=associated_task_id,
                        event_id=request.get("event_id", "unknown"),
                        status=AgentTaskLifecycleStatus.MCP_EXECUTOR,
                        node_name="mcp_executor",
                        details=f"Entering MCP executor for tool {request.get('tool_name')}",
                        metadata={"mcp_request": request}
                    )
                
                success = await self._execute_mcp_request(state, request)
                
                # Check if this completes the AgentTask
                if associated_task_id and success:
                    # Mark AgentTask as completed and log provenance
                    log_agent_task_provenance(state, associated_task_id, AgentTaskLifecycleStatus.COMPLETED, logger)
                    logger.info(f"MCPExecutor: AgentTask {associated_task_id} completed successfully")
                elif associated_task_id and not success:
                    # Mark AgentTask as error
                    log_agent_task_provenance(state, associated_task_id, AgentTaskLifecycleStatus.ERROR, logger)
                    logger.info(f"MCPExecutor: AgentTask {associated_task_id} failed with error")
            
            # Clear processed requests
            state["pending_mcp_requests"] = []
            logger.info("MCPExecutor: Cleared all pending MCP requests")
        
        # Execute tool calls based on recent decisions (legacy)
        for decision in state["recent_decisions"][-5:]:  # Check last 5 decisions
            if decision.decision_type == "update_event" and "event_id" in decision.metadata:
                await self._update_event_info(state, decision.metadata)
            elif decision.decision_type == "create_reminder" and "event_id" in decision.metadata:
                await self._create_event_reminder(state, decision.metadata)
            elif decision.decision_type == "test_services":
                await self._test_service_integration(state)
    
    async def _execute_mcp_request(self, state: AgentState, request: Dict[str, Any]) -> bool:
        """Execute a specific MCP request through the gateway and return success status"""
        tool_name = request.get("tool_name")
        arguments = request.get("arguments", {})
        event_id = request.get("event_id")
        
        self.log_execution(state, f"Executing MCP request via gateway: {tool_name} with args: {arguments}")
        
        try:
            # Route through gateway based on tool_name from reasoning node
            if tool_name == "event_manager":
                # Map to specific event_manager action and prepare arguments
                actual_tool_name = self._map_event_manager_tool(arguments)
                prepared_args = self._prepare_tool_arguments("event_manager", arguments)
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
                
                # If create_event was successful, also save to guild_data
                if actual_tool_name == "create_event" and result.get("success"):
                    try:
                        self.log_execution(state, "Create event successful, now saving to guild_data")
                        
                        # Extract data for guild_data save
                        event_data = arguments.get("event_data", {})
                        interaction_data = arguments.get("interaction_data", {})
                        
                        # Use consistent event_id (should be the same as Discord message_id now)
                        mcp_event_id = result.get("data", {}).get("event", {}).get("event_id")
                        save_event_id = str(mcp_event_id) if mcp_event_id else str(event_data.get("message_id", "unknown"))
                        save_guild_id = str(interaction_data.get("guild_id", "unknown"))
                        
                        # Prepare complete event data for saving
                        complete_event_data = {
                            **event_data,
                            **interaction_data,
                            "mcp_event_id": mcp_event_id,
                            "mcp_event_created_at": result.get("data", {}).get("event", {}).get("created_at"),
                            "discord_message_id": event_data.get("message_id"),  # Keep Discord message ID as metadata
                            "saved_from_agent": True
                        }
                        
                        # Call save_event_to_guild_data
                        save_result = await self.call_mcp_tool("save_event_to_guild_data", {
                            "event_id": save_event_id,
                            "guild_id": save_guild_id,
                            "event_data": complete_event_data
                        })
                        
                        if save_result.get("success"):
                            self.log_execution(state, f"Event saved to guild_data successfully: {save_result.get('data', {}).get('file_path', 'unknown path')}")
                        else:
                            self.log_execution(state, f"Failed to save event to guild_data: {save_result.get('message', 'Unknown error')}", "error")
                            
                    except Exception as e:
                        self.log_execution(state, f"Error saving event to guild_data: {e}", "error")
                
            elif tool_name == "rsvp":
                # Map to specific rsvp action and prepare arguments  
                actual_tool_name = self._map_rsvp_tool(arguments)
                prepared_args = self._prepare_tool_arguments("rsvp", arguments)
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
                
            elif tool_name == "guild_manager":
                # Map to specific guild_manager action and prepare arguments
                actual_tool_name = self._map_guild_manager_tool(arguments)
                prepared_args = self._prepare_tool_arguments("guild_manager", arguments)
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
                
            elif tool_name == "photo_vibe_check":
                # Map to specific photo_vibe_check action and prepare arguments
                logger.info("=== ROUTING TO photo_vibe_check ===")
                logger.info(f"Original arguments: {arguments}")
                actual_tool_name = self._map_photo_vibe_check_tool(arguments)
                logger.info(f"Mapped tool name: {actual_tool_name}")
                prepared_args = self._prepare_tool_arguments("photo_vibe_check", arguments)
                logger.info(f"Prepared arguments: {prepared_args}")
                logger.info(f"About to call MCP tool: {actual_tool_name}")
                logger.info(f"Final prepared args before call: {prepared_args}")
                logger.info(f"Prepared args keys: {list(prepared_args.keys())}")
                if 'action' in prepared_args:
                    logger.error(f"ERROR: 'action' parameter still in prepared_args! This will cause validation error.")
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
                logger.info(f"MCP tool result: {result}")
                
            elif tool_name == "vibe_bit":
                # Map to specific vibe_bit action and prepare arguments
                actual_tool_name = self._map_vibe_bit_tool(arguments)
                prepared_args = self._prepare_tool_arguments("vibe_bit", arguments)
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
                
            else:
                # Direct tool call through gateway
                actual_tool_name = tool_name
                prepared_args = arguments
                result = await self.call_mcp_tool(actual_tool_name, prepared_args)
            
            # Record the tool call
            tool_call = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool": tool_name,
                "actual_tool": actual_tool_name if 'actual_tool_name' in locals() else tool_name,
                "parameters": arguments,
                "result": result,
                "event_id": event_id,
                "routed_via": "gateway"
            }
            state["tool_call_history"].append(tool_call)
            
            success = result.get("success", False)
            if success:
                self.log_execution(state, f"MCP tool {tool_name} executed successfully via gateway")
            else:
                self.log_execution(state, f"MCP tool {tool_name} failed: {result.get('error', 'Unknown error')}", "error")
            
            return success
                
        except Exception as e:
            self.log_execution(state, f"Failed to execute MCP request {tool_name}: {e}", "error")
            return False
    
    def _map_event_manager_tool(self, arguments: Dict[str, Any]) -> str:
        """Map event_manager request to specific gateway tool name"""
        action = arguments.get("action", "get_event")
        
        # Map actions to actual gateway tool names
        action_mapping = {
            "create_event": "create_event",
            "update_event": "update_event", 
            "delete_event": "delete_event",
            "get_event": "get_event",
            "list_events": "list_all_events",
            "list_all_events": "list_all_events",  # Direct mapping
            "get_events_by_creator": "get_events_by_creator",
            "get_events_by_status": "get_events_by_status",
            "get_event_analytics": "get_event_analytics",
            "search_events": "search_events",
            "get_event_stats": "get_event_stats",
            "save_event_to_guild_data": "save_event_to_guild_data"
        }
        
        return action_mapping.get(action, "get_event")
    
    def _map_rsvp_tool(self, arguments: Dict[str, Any]) -> str:
        """Map rsvp request to specific gateway tool name"""
        action = arguments.get("action", "get_event_rsvps")
        
        # Map actions to actual gateway tool names
        action_mapping = {
            "create_rsvp": "create_rsvp",
            "get_rsvp": "get_rsvp",
            "update_rsvp": "update_rsvp",
            "delete_rsvp": "delete_rsvp",
            "process_rsvp": "process_rsvp",
            "get_user_rsvp_for_event": "get_user_rsvp_for_event",
            "get_event_rsvps": "get_event_rsvps",
            "get_user_rsvps": "get_user_rsvps",
            "update_user_rsvp": "update_user_rsvp",
            "get_rsvp_analytics": "get_rsvp_analytics",
            "list_events_with_rsvps": "list_events_with_rsvps",
            "get_rsvp_stats": "get_rsvp_stats"
        }
        
        return action_mapping.get(action, "get_event_rsvps")
    
    def _map_guild_manager_tool(self, arguments: Dict[str, Any]) -> str:
        """Map guild_manager request to specific gateway tool name"""
        action = arguments.get("action", "get_guild_info")
        
        # Map actions to actual gateway tool names
        action_mapping = {
            "register_guild": "register_guild",
            "deregister_guild": "deregister_guild",
            "get_guild_info": "get_guild_info",
            "list_guilds": "list_guilds",
            "update_guild_settings": "update_guild_settings",
            "get_guild_stats": "get_guild_stats"
        }
        
        return action_mapping.get(action, "get_guild_info")
    
    def _map_photo_vibe_check_tool(self, arguments: Dict[str, Any]) -> str:
        """Map photo_vibe_check request to specific gateway tool name"""
        action = arguments.get("action", "get_photo_status")
        logger.info(f"=== _map_photo_vibe_check_tool CALLED ===")
        logger.info(f"Action from arguments: {action}")
        
        # Map actions to actual gateway tool names
        action_mapping = {
            "submit_photo_dm": "submit_photo_dm",
            "activate_photo_collection": "activate_photo_collection",
            "deactivate_photo_collection": "deactivate_photo_collection",
            "update_photo_settings": "update_photo_settings",
            "add_pre_event_photos": "add_pre_event_photos",
            "get_photo_status": "get_photo_status",
            "get_event_photo_summary": "get_event_photo_summary",
            "generate_event_slideshow": "generate_event_slideshow",
            "get_user_photo_history": "get_user_photo_history"
        }
        
        mapped_tool = action_mapping.get(action, "get_photo_status")
        logger.info(f"Mapped action '{action}' to tool '{mapped_tool}'")
        return mapped_tool
    
    def _map_vibe_bit_tool(self, arguments: Dict[str, Any]) -> str:
        """Map vibe_bit request to specific gateway tool name"""
        action = arguments.get("action", "get_vibe_canvas_stats")
        
        # Map actions to actual gateway tool names
        action_mapping = {
            "vibe_bit": "vibe_bit",
            "create_vibe_canvas": "create_vibe_canvas",
            "activate_vibe_canvas": "activate_vibe_canvas",
            "deactivate_vibe_canvas": "deactivate_vibe_canvas",
            "update_vibe_settings": "update_vibe_settings",
            "get_vibe_canvas_image": "get_vibe_canvas_image",
            "get_vibe_canvas_preview": "get_vibe_canvas_preview",
            "get_vibe_canvas_stats": "get_vibe_canvas_stats",
            "get_user_vibe_history": "get_user_vibe_history",
            "get_color_palettes": "get_color_palettes",
            "get_emoji_sets": "get_emoji_sets",
            "create_vibe_snapshot": "create_vibe_snapshot"
        }
        
        return action_mapping.get(action, "get_vibe_canvas_stats")
    
    def _prepare_tool_arguments(self, service_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for gateway tool call based on service and CloudEvent data"""
        if service_name == "event_manager":
            return self._prepare_event_manager_args(arguments)
        elif service_name == "rsvp":
            return self._prepare_rsvp_args(arguments)
        elif service_name == "guild_manager":
            return self._prepare_guild_manager_args(arguments)
        elif service_name == "photo_vibe_check":
            return self._prepare_photo_vibe_check_args(arguments)
        elif service_name == "vibe_bit":
            return self._prepare_vibe_bit_args(arguments)
        else:
            return arguments
    
    def _prepare_event_manager_args(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for event_manager tools"""
        action = arguments.get("action", "get_event")
        event_data = arguments.get("event_data", {})
        interaction_data = arguments.get("interaction_data", {})
        
        if action in ["list_events", "list_all_events"]:
            # For list_all_events, only pass valid parameters
            prepared_args = {}
            
            # Only include status if it's not None
            if arguments.get("status") is not None:
                prepared_args["status"] = arguments.get("status")
            
            # Always include limit with default value
            prepared_args["limit"] = arguments.get("limit", 100)
            
            return prepared_args
            
        elif action == "create_event":
            # Map Discord event data to MCP event_manager format
            title = event_data.get("topic", "Unknown Event")
            location = event_data.get("location")
            time_str = event_data.get("time")
            
            # Build description from available info
            desc_parts = []
            if location:
                desc_parts.append(f"Location: {location}")
            if time_str:
                desc_parts.append(f"Time: {time_str}")
            description = ", ".join(desc_parts) if desc_parts else None
            
            # Extract guild_id from arguments or metadata (similar to photo_vibe_check handling)
            metadata = arguments.get("metadata", {})
            
            create_args = {
                "title": title,
                "created_by": str(interaction_data.get("user_id", interaction_data.get("user_name", "Unknown"))),
                "guild_id": arguments.get("guild_id") or interaction_data.get("guild_id") or metadata.get("discord_guild_id"),
                "event_id": str(event_data.get("message_id")) if event_data.get("message_id") else None,
            }
            
            if description:
                create_args["description"] = description
            if location:
                create_args["location"] = location
                
            # Always add metadata
            create_args["metadata"] = {
                "discord_message_id": event_data.get("message_id"),
                "discord_thread_id": event_data.get("thread_id"),
                "discord_guild_id": interaction_data.get("guild_id"),
                "discord_channel_id": interaction_data.get("channel_id"),
                "discord_user_id": interaction_data.get("user_id"),
                "discord_user_name": interaction_data.get("user_name"),
                "source": "discord_create_event",
                "ambient_agent_processed": True,
                "original_time": time_str
            }
            
            # Only add start_time if it's in ISO format
            if time_str:
                try:
                    from datetime import datetime
                    parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    create_args["start_time"] = time_str
                except (ValueError, AttributeError):
                    logger.info(f"MCPExecutor: Skipping start_time parameter due to non-ISO format: '{time_str}'")
            
            return create_args
            
        elif action == "update_event":
            # Similar mapping for update_event
            event_data = arguments.get("event_data", {})
            interaction_data = arguments.get("interaction_data", {})
            
            # Extract guild_id from arguments or metadata (similar to photo_vibe_check handling)
            metadata = arguments.get("metadata", {})
            
            update_args = {
                "event_id": event_data.get("message_id", arguments.get("event_id", "unknown")),
                "user_id": interaction_data.get("user_id", "unknown"),
                "guild_id": arguments.get("guild_id") or interaction_data.get("guild_id") or metadata.get("discord_guild_id")
            }
            
            title = event_data.get("topic")
            if title:
                update_args["title"] = title
                
            location = event_data.get("location")
            time_str = event_data.get("time")
            
            desc_parts = []
            if location:
                desc_parts.append(f"Location: {location}")
            if time_str:
                desc_parts.append(f"Time: {time_str}")
            if desc_parts:
                update_args["description"] = ", ".join(desc_parts)
                
            if location:
                update_args["location"] = location
                
            if time_str:
                try:
                    from datetime import datetime
                    parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    update_args["start_time"] = time_str
                except (ValueError, AttributeError):
                    logger.info(f"MCPExecutor: Skipping start_time for update due to non-ISO format: '{time_str}'")
            
            update_args["metadata"] = {
                "updated_by": str(interaction_data.get("user_id", interaction_data.get("user_name", "Unknown"))),
                "discord_guild_id": interaction_data.get("guild_id"),
                "discord_channel_id": interaction_data.get("channel_id"),
                "discord_user_id": interaction_data.get("user_id"),
                "discord_user_name": interaction_data.get("user_name"),
                "source": "discord_update_event",
                "ambient_agent_processed": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return update_args
            
        elif action == "delete_event":
            interaction_data = arguments.get("interaction_data", {})
            
            # Extract guild_id from arguments or metadata (similar to photo_vibe_check handling)
            metadata = arguments.get("metadata", {})
            
            return {
                "event_id": arguments.get("event_id", "unknown"),
                "user_id": interaction_data.get("user_id", "unknown"),
                "guild_id": arguments.get("guild_id") or interaction_data.get("guild_id") or metadata.get("discord_guild_id"),
                "metadata": {
                    "deleted_by": interaction_data.get("user_name", "Unknown"),
                    "discord_guild_id": interaction_data.get("guild_id"),
                    "discord_channel_id": interaction_data.get("channel_id"),
                    "discord_user_id": interaction_data.get("user_id"),
                    "source": "discord_delete_event",
                    "ambient_agent_processed": True,
                    "deleted_at": datetime.now(timezone.utc).isoformat()
                }
            }
        
        elif action == "save_event_to_guild_data":
            return {
                "event_id": arguments.get("event_id", "unknown"),
                "guild_id": arguments.get("guild_id", "unknown"),
                "event_data": arguments.get("event_data", {})
            }
        
        # For other actions, return arguments as-is
        return arguments
    
    def _prepare_rsvp_args(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for rsvp tools"""
        action = arguments.get("action", "get_event_rsvps")
        
        if action == "process_rsvp":
            metadata = arguments.get("metadata", {})
            return {
                "guild_id": arguments.get("guild_id") or metadata.get("guild_id"),
                "event_id": arguments.get("event_id"),
                "user_id": arguments.get("user_id"),
                "rsvp_type": arguments.get("rsvp_type", "add"),
                "emoji": arguments.get("emoji"),
                "metadata": metadata
            }
        
        return arguments
    
    def _prepare_guild_manager_args(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for guild_manager tools"""
        action = arguments.get("action", "get_guild_info")
        
        if action == "register_guild":
            return {
                "guild_id": arguments.get("guild_id"),
                "guild_name": arguments.get("guild_name"),
                "channel_id": arguments.get("channel_id"),
                "channel_name": arguments.get("channel_name"),
                "user_id": arguments.get("user_id"),
                "user_name": arguments.get("user_name"),
                "metadata": arguments.get("metadata", {})
            }
        elif action == "deregister_guild":
            return {
                "guild_id": arguments.get("guild_id"),
                "guild_name": arguments.get("guild_name"),
                "user_id": arguments.get("user_id"),
                "user_name": arguments.get("user_name"),
                "metadata": arguments.get("metadata", {})
            }
        
        return arguments
    
    def _prepare_photo_vibe_check_args(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for photo_vibe_check tools"""
        action = arguments.get("action", "get_photo_status")
        logger.info(f"=== _prepare_photo_vibe_check_args CALLED ===")
        logger.info(f"Action: {action}")
        logger.info(f"Input arguments: {arguments}")
        
        if action == "submit_photo_dm":
            # Extract guild_id from arguments or metadata (similar to RSVP handling)
            metadata = arguments.get("metadata", {})
            prepared_args = {
                "guild_id": arguments.get("guild_id") or metadata.get("guild_id"),
                "event_id": arguments.get("event_id", "unknown"),
                "user_id": arguments.get("user_id"),
                "photo_url": arguments.get("photo_url"),
                "metadata": metadata
            }
            logger.info(f"Prepared args for submit_photo_dm: {prepared_args}")
            return prepared_args
        
        elif action == "add_pre_event_photos":
            # Extract guild_id from arguments or metadata (similar to RSVP handling)
            metadata = arguments.get("metadata", {})
            prepared_args = {
                "event_id": arguments.get("event_id"),
                "admin_user_id": arguments.get("admin_user_id"),
                "photo_urls": arguments.get("photo_urls", []),
                "guild_id": arguments.get("guild_id") or metadata.get("guild_id"),
                "metadata": metadata
            }
            logger.info(f"Prepared args for add_pre_event_photos: {prepared_args}")
            return prepared_args
        
        logger.info(f"Using original arguments for action: {action}")
        return arguments
    
    def _prepare_vibe_bit_args(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for vibe_bit tools"""
        # Most vibe_bit arguments can be passed through as-is
        return arguments

    # Legacy handler methods - simplified to route through gateway
    async def _handle_event_manager_request(self, state: AgentState, arguments: Dict[str, Any], event_id: str):
        """Handle event_manager specific requests via gateway (deprecated - use _execute_mcp_request)"""
        logger.warning("Using deprecated _handle_event_manager_request - should use _execute_mcp_request instead")
        
        # Convert to new format and route through gateway
        request = {
            "tool_name": "event_manager",
            "arguments": arguments,
            "event_id": event_id
        }
        
        await self._execute_mcp_request(state, request)
    
    async def _handle_create_event(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle create_event requests"""
        event_data = arguments["event_data"]
        interaction_data = arguments.get("interaction_data", {})
        
        # Log CloudEvent to MCP mapping
        logger.info(f"MCPExecutor: Creating event via MCP - event_data={event_data}, interaction_data={interaction_data}")
        
        # Map Discord event data to MCP event_manager format
        title = event_data.get("topic", "Unknown Event")
        location = event_data.get("location")
        time_str = event_data.get("time")
        
        # Build description from available info
        desc_parts = []
        if location:
            desc_parts.append(f"Location: {location}")
        if time_str:
            desc_parts.append(f"Time: {time_str}")
        description = ", ".join(desc_parts) if desc_parts else None
        
        create_args = {
            "title": title,
            "created_by": str(interaction_data.get("user_id", interaction_data.get("user_name", "Unknown"))),  # Use user_id as required by tool
        }
        
        # Only add optional parameters if they have meaningful values
        if description:
            create_args["description"] = description
        if location:
            create_args["location"] = location
            
        # Always add metadata
        create_args["metadata"] = {
            "discord_message_id": event_data.get("message_id"),
            "discord_thread_id": event_data.get("thread_id"),
            "discord_guild_id": interaction_data.get("guild_id"),
            "discord_channel_id": interaction_data.get("channel_id"),
            "discord_user_id": interaction_data.get("user_id"),
            "discord_user_name": interaction_data.get("user_name"),  # Keep name in metadata
            "source": "discord_create_event",
            "ambient_agent_processed": True,
            "original_time": time_str  # Store original time for reference
        }
        
        # Only add start_time if it's in ISO format, otherwise omit it
        if time_str:
            try:
                # Try to parse as ISO datetime
                from datetime import datetime
                parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                create_args["start_time"] = time_str
            except (ValueError, AttributeError):
                # If not ISO format, don't include start_time parameter
                # The time info is still available in description and metadata
                logger.info(f"MCPExecutor: Skipping start_time parameter due to non-ISO format: '{time_str}'")
        
        # Call the create_event tool via gateway
        result = await self.call_mcp_tool("create_event", create_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "create_event",
            "parameters": create_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "create_event"
        }
        state["tool_call_history"].append(tool_call)
        
        # Log based on actual result
        if result.get("success", False):
            self.log_execution(state, f"Event created via MCP: {event_data.get('topic', 'Unknown')}")
        else:
            self.log_execution(state, f"Failed to create event via MCP: {event_data.get('topic', 'Unknown')} - Error: {result.get('error', 'Unknown error')}", "error")
        
        return result
    
    async def _handle_update_event(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle update_event requests"""
        from datetime import datetime, timezone
        
        event_data = arguments.get("event_data", {})
        interaction_data = arguments.get("interaction_data", {})
        metadata = arguments.get("metadata", {})
        
        # Log the raw arguments for debugging
        logger.info(f"MCPExecutor: Update event raw arguments - event_data={event_data}, interaction_data={interaction_data}, metadata={metadata}")
        
        # If event_data is empty, try to extract info from metadata
        if not event_data and metadata:
            logger.info("MCPExecutor: Event data is empty, attempting to extract from metadata")
            # Extract available information from metadata
            original_topic = metadata.get("original_topic")
            updated_fields = metadata.get("updated_fields", [])
            
            if original_topic:
                # Use original topic as a fallback for missing data
                event_data = {"topic": original_topic}
                logger.info(f"MCPExecutor: Using metadata to populate event_data - topic: '{original_topic}', updated_fields: {updated_fields}")
        
        # Build update arguments, only including non-empty values
        update_args = {
            "event_id": event_data.get("message_id", event_id)
        }
        
        # Only add fields that have actual values
        title = event_data.get("topic")
        if title:
            update_args["title"] = title
            
        location = event_data.get("location")
        time_str = event_data.get("time")
        
        # Build description only if we have meaningful data
        desc_parts = []
        if location:
            desc_parts.append(f"Location: {location}")
        if time_str:
            desc_parts.append(f"Time: {time_str}")
        if desc_parts:
            update_args["description"] = ", ".join(desc_parts)
            
        if location:
            update_args["location"] = location
            
        # Handle start_time with ISO format validation (same as create_event)
        if time_str:
            try:
                parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                update_args["start_time"] = time_str
            except (ValueError, AttributeError):
                logger.info(f"MCPExecutor: Skipping start_time for update due to non-ISO format: '{time_str}'")
        
        # Always include metadata
        update_args["metadata"] = {
            "updated_by": str(interaction_data.get("user_id", interaction_data.get("user_name", "Unknown"))),
            "discord_guild_id": interaction_data.get("guild_id"),
            "discord_channel_id": interaction_data.get("channel_id"),
            "discord_user_id": interaction_data.get("user_id"),
            "discord_user_name": interaction_data.get("user_name"),
            "source": "discord_update_event",
            "ambient_agent_processed": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Call the update_event tool via gateway
        result = await self.call_mcp_tool("update_event", update_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "update_event",
            "parameters": update_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "update_event"
        }
        state["tool_call_history"].append(tool_call)
        
        # Log based on actual result
        event_title = title or event_data.get('topic', 'Unknown')
        if result.get("success", False):
            self.log_execution(state, f"Event updated via MCP: {event_title}")
        else:
            self.log_execution(state, f"Failed to update event via MCP: {event_title} - Error: {result.get('error', 'Unknown error')}", "error")
        
        return result
    
    async def _handle_delete_event(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle delete_event requests"""
        interaction_data = arguments.get("interaction_data", {})
        
        # Map delete data to MCP event_manager format
        delete_args = {
            "event_id": arguments.get("event_id", event_id),
            "metadata": {
                "deleted_by": interaction_data.get("user_name", "Unknown"),
                "discord_guild_id": interaction_data.get("guild_id"),
                "discord_channel_id": interaction_data.get("channel_id"),
                "discord_user_id": interaction_data.get("user_id"),
                "source": "discord_delete_event",
                "ambient_agent_processed": True,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Call the delete_event tool via gateway
        result = await self.call_mcp_tool("delete_event", delete_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "delete_event",
            "parameters": delete_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "delete_event"
        }
        state["tool_call_history"].append(tool_call)
        
        self.log_execution(state, f"Event deleted via MCP: {event_id}")
        return result
    
    async def _handle_rsvp_request(self, state: AgentState, arguments: Dict[str, Any], event_id: str):
        """Handle RSVP specific requests (deprecated - use _execute_mcp_request)"""
        logger.warning("Using deprecated _handle_rsvp_request - should use _execute_mcp_request instead")
        
        # Convert to new format and route through gateway
        request = {
            "tool_name": "rsvp",
            "arguments": arguments,
            "event_id": event_id
        }
        
        return await self._execute_mcp_request(state, request)
    
    async def _handle_process_rsvp(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle RSVP processing with LLM scoring"""
        
        # Map CloudEvent arguments to MCP tool format
        metadata = arguments.get("metadata", {})
        process_args = {
            "guild_id": arguments.get("guild_id") or metadata.get("guild_id"),
            "event_id": arguments.get("event_id", event_id),
            "user_id": arguments.get("user_id"),
            "rsvp_type": arguments.get("rsvp_type", "add"),
            "emoji": arguments.get("emoji"),
            "metadata": metadata
        }
        
        # Call the process_rsvp tool via gateway
        result = await self.call_mcp_tool("process_rsvp", process_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "process_rsvp",
            "parameters": process_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "process_rsvp"
        }
        state["tool_call_history"].append(tool_call)
        
        # Store RSVP result in agent state for future reference
        if result.get("success") and "result" in result:
            rsvp_result = result["result"]
            attendance_score = rsvp_result.get("attendance_score", 0.5)
            
            # Update agent state with attendance prediction
            if "rsvp_predictions" not in state:
                state["rsvp_predictions"] = {}
            
            state["rsvp_predictions"][f"{event_id}_{process_args['user_id']}"] = {
                "attendance_score": attendance_score,
                "emoji": process_args["emoji"],
                "confidence": rsvp_result.get("confidence", 0.5),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
        
        self.log_execution(state, f"RSVP processed via MCP: {process_args.get('emoji', 'unknown')} for event {event_id}")
        return result
    
    async def _handle_guild_manager_request(self, state: AgentState, arguments: Dict[str, Any], event_id: str):
        """Handle guild_manager specific requests (deprecated - use _execute_mcp_request)"""
        logger.warning("Using deprecated _handle_guild_manager_request - should use _execute_mcp_request instead")
        
        # Convert to new format and route through gateway
        request = {
            "tool_name": "guild_manager",
            "arguments": arguments,
            "event_id": event_id
        }
        
        return await self._execute_mcp_request(state, request)
    
    async def _handle_register_guild(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle guild registration requests"""
        
        # Map CloudEvent arguments to MCP tool format
        register_args = {
            "guild_id": arguments.get("guild_id"),
            "guild_name": arguments.get("guild_name"),
            "channel_id": arguments.get("channel_id"),
            "channel_name": arguments.get("channel_name"),
            "user_id": arguments.get("user_id"),
            "user_name": arguments.get("user_name"),
            "metadata": arguments.get("metadata", {})
        }
        
        # Call the register_guild tool via gateway
        result = await self.call_mcp_tool("register_guild", register_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "register_guild",
            "parameters": register_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "register_guild"
        }
        state["tool_call_history"].append(tool_call)
        
        # Update agent state with guild registration
        if result.get("success"):
            if "registered_guilds" not in state:
                state["registered_guilds"] = {}
            
            state["registered_guilds"][register_args["guild_id"]] = {
                "guild_name": register_args["guild_name"],
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "registered_by": register_args["user_name"]
            }
        
        self.log_execution(state, f"Guild registered via MCP: {register_args.get('guild_name', 'unknown')}")
        return result
    
    async def _handle_deregister_guild(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle guild deregistration requests"""
        
        # Map CloudEvent arguments to MCP tool format
        deregister_args = {
            "guild_id": arguments.get("guild_id"),
            "guild_name": arguments.get("guild_name"),
            "user_id": arguments.get("user_id"),
            "user_name": arguments.get("user_name"),
            "metadata": arguments.get("metadata", {})
        }
        
        # Call the deregister_guild tool via gateway
        result = await self.call_mcp_tool("deregister_guild", deregister_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "deregister_guild",
            "parameters": deregister_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "deregister_guild"
        }
        state["tool_call_history"].append(tool_call)
        
        # Update agent state to remove guild registration
        if result.get("success") and "registered_guilds" in state:
            guild_id = deregister_args["guild_id"]
            if guild_id in state["registered_guilds"]:
                del state["registered_guilds"][guild_id]
        
        self.log_execution(state, f"Guild deregistered via MCP: {deregister_args.get('guild_name', 'unknown')}")
        return result
    
    async def _handle_photo_vibe_check_request(self, state: AgentState, arguments: Dict[str, Any], event_id: str):
        """Handle photo_vibe_check specific requests (deprecated - use _execute_mcp_request)"""
        logger.warning("Using deprecated _handle_photo_vibe_check_request - should use _execute_mcp_request instead")
        
        # Convert to new format and route through gateway
        request = {
            "tool_name": "photo_vibe_check",
            "arguments": arguments,
            "event_id": event_id
        }
        
        return await self._execute_mcp_request(state, request)
    
    async def _handle_submit_photo_dm(self, state: AgentState, arguments: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Handle photo submission from DM for vibe check"""
        
        # Map CloudEvent arguments to MCP tool format
        submit_args = {
            "guild_id": arguments.get("guild_id"),
            "event_id": arguments.get("event_id") or "unknown",  # Default if no specific event
            "user_id": arguments.get("user_id"),
            "photo_url": arguments.get("photo_url"),
            "metadata": arguments.get("metadata", {})
        }
        
        # Call the submit_photo_dm tool via gateway
        result = await self.call_mcp_tool("submit_photo_dm", submit_args)
        
        # Record the tool call
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "submit_photo_dm",
            "parameters": submit_args,
            "result": result,
            "event_id": event_id,
            "cloudevent_action": "submit_photo_dm"
        }
        state["tool_call_history"].append(tool_call)
        
        self.log_execution(state, f"Photo submission processed via MCP: {submit_args.get('photo_url', 'unknown')}")
        return result
    
    async def _update_event_info(self, state: AgentState, metadata: Dict[str, Any]):
        """Update event information via MCP gateway"""
        event_id = metadata.get("event_id")
        if not event_id:
            return
        
        try:
            # Call event manager MCP service via gateway
            self.log_execution(state, f"Fetching event info for {event_id}")
            
            result = await self.call_mcp_tool("get_event", {"event_id": event_id})
            
            # Record the tool call
            tool_call = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool": "get_event",
                "parameters": {"event_id": event_id},
                "service": "gateway",
                "status": "success" if result.get("success") else "failed",
                "result": result
            }
            state["tool_call_history"].append(tool_call)
            
            if result.get("success"):
                self.log_execution(state, f"Successfully fetched event {event_id}")
            else:
                self.log_execution(state, f"Failed to fetch event {event_id}: {result.get('error')}", "warning")
            
        except Exception as e:
            self.log_execution(state, f"Failed to update event {event_id}: {e}", "error")
    
    async def _create_event_reminder(self, state: AgentState, metadata: Dict[str, Any]):
        """Create event reminder via MCP"""
        event_id = metadata.get("event_id")
        reminder_type = metadata.get("reminder_type", "general")
        
        try:
            self.log_execution(state, f"Creating {reminder_type} reminder for event {event_id}")
            
            # Record the tool call
            tool_call = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool": "create_reminder",
                "parameters": {"event_id": event_id, "type": reminder_type},
                "service": "event_manager",
                "status": "simulated"
            }
            state["tool_call_history"].append(tool_call)
            
        except Exception as e:
            self.log_execution(state, f"Failed to create reminder for {event_id}: {e}", "error")
    
    async def _refresh_event_cache(self, state: AgentState):
        """Refresh event context cache with latest information"""
        # Get list of events we care about (from active timers, recent activity)
        relevant_event_ids = set()
        
        # Add events from active timers
        for timer in state["active_timers"]:
            relevant_event_ids.add(timer.event_id)
        
        # Add events from recent activity
        for decision in state["recent_decisions"][-10:]:
            if "event_id" in decision.metadata:
                relevant_event_ids.add(decision.metadata["event_id"])
        
        # Refresh cache for relevant events
        for event_id in relevant_event_ids:
            try:
                # In a real implementation, call MCP service
                # For now, just log the intent
                self.log_execution(state, f"Refreshing cache for event {event_id}")
                
                # Simulate cache update
                if event_id not in state["event_cache"]:
                    from tlt.agents.ambient_event_agent.state.state import EventContext
                    state["event_cache"][event_id] = EventContext(
                        event_id=event_id,
                        event_title=f"Event {event_id}",
                        created_by="system",
                        rsvp_count=0
                    )
                
            except Exception as e:
                self.log_execution(state, f"Failed to refresh cache for {event_id}: {e}", "error")
    
    async def _check_service_health(self, state: AgentState):
        """Check health of MCP gateway and available tools"""
        available_tools = []
        
        try:
            # Check gateway health by calling ping
            result = await self.call_mcp_tool("ping", {})
            if result.get("success"):
                self.log_execution(state, "Gateway health check passed")
                # Get available tools from gateway
                tools_result = await self.call_mcp_tool("get_available_tools", {})
                if tools_result.get("success") and "result" in tools_result:
                    # Extract tool names from all services
                    # The result is a CallToolResult, so we need to get the structured_content or data
                    call_result = tools_result["result"]
                    if hasattr(call_result, 'structured_content') and call_result.structured_content:
                        services_info = call_result.structured_content
                    elif hasattr(call_result, 'data') and call_result.data:
                        services_info = call_result.data
                    else:
                        services_info = {}
                    
                    for service_name, service_info in services_info.items():
                        if "tools" in service_info:
                            available_tools.extend(service_info["tools"])
            else:
                self.log_execution(state, f"Gateway health check failed: {result.get('error')}", "warning")
                
        except Exception as e:
            self.log_execution(state, f"Gateway health check failed: {e}", "warning")
        
        state["available_tools"] = available_tools
        
        # Limit tool call history
        if len(state["tool_call_history"]) > 100:
            state["tool_call_history"] = state["tool_call_history"][-50:]
    
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Make an MCP tool call through the gateway using FastMCP Client with StreamableHttpTransport"""
        try:
            # Log every MCP tool call for flow tracking
            logger.info(f"=== call_mcp_tool CALLED ===")
            logger.info(f"Tool name: {tool_name}")
            logger.info(f"Parameters: {parameters}")
            logger.info(f"Parameter keys: {list(parameters.keys())}")
            
            # Create FastMCP Client with StreamableHttpTransport for gateway
            transport = StreamableHttpTransport(url=self.gateway_url)
            
            async with Client(transport, client_info=self.client_info) as client:
                # Call the tool using FastMCP Client through gateway
                result = await client.call_tool(
                    name=tool_name,
                    arguments=parameters
                )
                
                # Wrap result in standard format
                wrapped_result = {
                    "success": True,
                    "result": result,
                    "tool": tool_name,
                    "service": "gateway",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Log result for flow tracking
                logger.info(f"MCPExecutor: MCP tool '{tool_name}' result via gateway: {wrapped_result}")
                return wrapped_result
                
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "parameters": parameters,
                "service": "gateway",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            logger.error(f"MCPExecutor: MCP tool '{tool_name}' error via gateway: {error_result}")
            return error_result
    
    
    
    async def _test_service_integration(self, state: AgentState):
        """Test integration with MCP services via gateway"""
        try:
            self.log_execution(state, "Testing MCP service integration via gateway")
            
            # Test 1: Ping gateway
            ping_result = await self.call_mcp_tool("ping", {})
            self.log_execution(state, f"Gateway ping result: {ping_result.get('success', False)}")
            
            # Test 2: Create a test event through gateway
            test_event_result = await self.call_mcp_tool("create_event", {
                "title": "Test Event from Agent",
                "description": "Created by ambient event agent for testing",
                "created_by": "ambient_agent",
                "start_time": "2024-01-01T12:00:00Z",
                "location": "Virtual"
            })
            self.log_execution(state, f"Create event result: {test_event_result.get('success', False)}")
            
            # Test 3: Create RSVP if event creation succeeded
            if test_event_result.get("success") and "result" in test_event_result:
                event_data = test_event_result["result"]
                # Try to extract event ID from result
                event_id = event_data.get("event_id") or event_data.get("id")
                if event_id:
                    rsvp_result = await self.call_mcp_tool("create_rsvp", {
                        "event_id": event_id,
                        "user_id": "ambient_agent",
                        "emoji": "✅"
                    })
                    self.log_execution(state, f"Create RSVP result: {rsvp_result.get('success', False)}")
            
            # Record test completion
            tool_call = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool": "integration_test",
                "parameters": {},
                "service": "gateway",
                "status": "completed",
                "results": {
                    "ping": ping_result,
                    "create_event": test_event_result
                }
            }
            state["tool_call_history"].append(tool_call)
            
        except Exception as e:
            self.log_execution(state, f"Service integration test failed: {e}", "error")