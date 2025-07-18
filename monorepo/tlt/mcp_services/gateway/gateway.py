import os
from loguru import logger
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastmcp import FastMCP
from tlt.mcp_services.gateway.models import ProxyConfig, UserRole, AuthContext, DEFAULT_RBAC_RULES
from tlt.mcp_services.gateway.rbac import RBACMiddleware, default_auth_resolver

# Using loguru logger imported above

class MCPGateway:
    """FastMCP 2.0+ Gateway with native proxying and RBAC middleware"""
    
    def __init__(self):
        self.mcp = FastMCP("TLT MCP Gateway")
        self.rbac = RBACMiddleware(DEFAULT_RBAC_RULES)
        self.rbac.set_auth_resolver(default_auth_resolver)
        self.proxy_clients = {}  # Store proxy clients
        
        # Configure proxy services
        self.proxy_configs = {
            'event_manager': ProxyConfig(
                name="Event Manager",
                url=os.getenv('EVENT_MANAGER_URL', 'http://localhost:8004'),
                transport="streamable-http",
                enabled=True,
                tools=[
                    "create_event", "get_event", "update_event", "delete_event",
                    "list_all_events", "get_events_by_creator", "get_events_by_status",
                    "get_event_analytics", "search_events", "get_event_stats"
                ]
            ),
            'rsvp': ProxyConfig(
                name="RSVP Service",
                url=os.getenv('RSVP_URL', 'http://localhost:8007'),
                transport="streamable-http",
                enabled=True,
                tools=[
                    "create_rsvp", "get_rsvp", "update_rsvp", "delete_rsvp",
                    "get_user_rsvp_for_event", "get_event_rsvps", "get_user_rsvps",
                    "update_user_rsvp", "get_rsvp_analytics", "list_events_with_rsvps",
                    "get_rsvp_stats"
                ]
            ),
            'photo_vibe_check': ProxyConfig(
                name="Photo Vibe Check",
                url=os.getenv('PHOTO_VIBE_CHECK_URL', 'http://localhost:8005'),
                transport="streamable-http",
                enabled=True,
                tools=[
                    "submit_photo_dm", "activate_photo_collection", "deactivate_photo_collection",
                    "update_photo_settings", "add_pre_event_photos", "get_photo_status",
                    "get_event_photo_summary", "generate_event_slideshow", "get_user_photo_history"
                ]
            ),
            'vibe_bit': ProxyConfig(
                name="Vibe Bit Canvas",
                url=os.getenv('VIBE_BIT_URL', 'http://localhost:8006'),
                transport="streamable-http",
                enabled=True,
                tools=[
                    "create_canvas", "get_canvas_info", "update_canvas_settings",
                    "activate_canvas", "deactivate_canvas", "place_element",
                    "view_canvas_progress", "get_canvas_image", "get_user_contributions",
                    "get_canvas_analytics"
                ]
            )
        }
        
        # Setup will be done asynchronously
        self._setup_gateway_tools()
    
    async def _setup_proxies(self):
        """Set up MCP proxy connections to backend services"""
        from fastmcp import Client
        from fastmcp.transports.http import PythonHttpTransport
        
        for service_name, config in self.proxy_configs.items():
            if config.enabled:
                try:
                    logger.info(f"Setting up proxy for {config.name} at {config.url}")
                    
                    # Create client for the backend service
                    client = Client(
                        transport=PythonHttpTransport(config.url)
                    )
                    
                    # Create proxy using FastMCP.as_proxy()
                    proxy = await FastMCP.as_proxy(
                        client, 
                        name=f"{config.name} Proxy"
                    )
                    
                    # Merge proxy tools into main gateway
                    # Note: This is a simplified approach - in production you'd want more sophisticated merging
                    for tool_name in config.tools:
                        if hasattr(proxy, tool_name):
                            setattr(self.mcp, tool_name, getattr(proxy, tool_name))
                    
                    logger.info(f"Proxy configured for {config.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to setup proxy for {config.name}: {e}")
                    config.enabled = False
    
    def _setup_middleware(self):
        """Set up RBAC middleware for all tools"""
        
        @self.mcp.middleware
        def auth_middleware(tool_name: str, **kwargs):
            """RBAC middleware that runs before every tool call"""
            logger.debug(f"RBAC check for tool: {tool_name}")
            
            # Extract auth context
            auth_context = self.rbac._extract_auth_context(kwargs)
            
            if not auth_context:
                logger.error(f"No authentication context for tool {tool_name}")
                raise PermissionError("Authentication required")
            
            # Check permissions
            if not self.rbac.check_permission(tool_name, auth_context):
                logger.error(f"Access denied for user {auth_context.user_id} to tool {tool_name}")
                raise PermissionError(f"Access denied to tool '{tool_name}' for role '{auth_context.role.value}'")
            
            logger.debug(f"Access granted for {auth_context.user_id} ({auth_context.role.value}) to {tool_name}")
            
            # Add auth context to kwargs for downstream services
            kwargs['auth_context'] = auth_context.dict()
            
            return kwargs
    
    def _setup_gateway_tools(self):
        """Set up gateway-specific management tools"""
        
        @self.mcp.tool()
        def get_gateway_status() -> Dict[str, Any]:
            """Get status of the MCP gateway and all proxied services"""
            status = {
                "gateway": {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "2.0.0"
                },
                "proxied_services": {}
            }
            
            for service_name, config in self.proxy_configs.items():
                status["proxied_services"][service_name] = {
                    "name": config.name,
                    "url": config.url,
                    "enabled": config.enabled,
                    "tools_count": len(config.tools)
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
                    "available_services": list(self.proxy_configs.keys())
                }
                
            except ValueError as e:
                return {
                    "error": f"Invalid role: {role}. Valid roles: {[r.value for r in UserRole]}"
                }
        
        @self.mcp.tool()
        def get_rbac_rules() -> Dict[str, Any]:
            """Get current RBAC rules configuration"""
            return {
                "rbac_rules": [
                    {
                        "tool_pattern": rule.tool_pattern,
                        "allowed_roles": [role.value for role in rule.allowed_roles],
                        "description": rule.description
                    }
                    for rule in self.rbac.rbac_rules
                ],
                "user_roles": [role.value for role in UserRole]
            }
        
        @self.mcp.tool()
        def get_available_tools() -> Dict[str, Any]:
            """Get all available tools from proxied services"""
            all_tools = {}
            
            for service_name, config in self.proxy_configs.items():
                if config.enabled:
                    all_tools[service_name] = {
                        "service_name": config.name,
                        "url": config.url,
                        "tools": config.tools
                    }
            
            # Add gateway tools
            all_tools["gateway"] = {
                "service_name": "Gateway Management",
                "url": "local",
                "tools": [
                    "get_gateway_status",
                    "get_user_permissions", 
                    "get_rbac_rules",
                    "get_available_tools"
                ]
            }
            
            return all_tools
    
    def get_mcp_instance(self) -> FastMCP:
        """Get the configured FastMCP instance"""
        return self.mcp