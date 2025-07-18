"""
Simplified Gateway for MCP Inspector Testing
This version removes RBAC requirements for testing purposes
"""

import os
import sys
from loguru import logger
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP

class SimpleTestGateway:
    """Simplified MCP Gateway for testing without RBAC"""
    
    def __init__(self):
        self.mcp = FastMCP("TLT MCP Gateway - Test")
        
        # Configure backend services
        self.backend_services = {
            'event_manager': {
                'name': 'Event Manager',
                'url': os.getenv('EVENT_MANAGER_URL', 'http://localhost:8004'),
                'status': 'offline'
            },
            'rsvp': {
                'name': 'RSVP Service', 
                'url': os.getenv('RSVP_URL', 'http://localhost:8007'),
                'status': 'offline'
            },
            'guild_manager': {
                'name': 'Guild Manager',
                'url': os.getenv('GUILD_MANAGER_URL', 'http://localhost:8009'),
                'status': 'offline'
            }
        }
        
        self._setup_test_tools()
    
    def _setup_test_tools(self):
        """Set up simple tools for testing"""
        
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
            return {
                "gateway": {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "2.0.0-test"
                },
                "backend_services": self.backend_services
            }
        
        @self.mcp.tool()
        def list_backend_services() -> Dict[str, Any]:
            """List all configured backend services"""
            return {
                "services": [
                    {
                        "name": service_name,
                        "display_name": service["name"],
                        "url": service["url"],
                        "status": service.get("status", "unknown")
                    }
                    for service_name, service in self.backend_services.items()
                ]
            }
        
        @self.mcp.tool()
        def echo(message: str) -> Dict[str, Any]:
            """Echo back a message"""
            return {
                "original_message": message,
                "echo": f"Gateway received: {message}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        logger.info("Test tools configured for MCP Gateway")
    
    def get_mcp_instance(self) -> FastMCP:
        """Get the configured FastMCP instance"""
        return self.mcp