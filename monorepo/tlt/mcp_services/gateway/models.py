from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone

class MCPRequestType(str, Enum):
    TOOL_CALL = "tool_call"
    AGENT_QUERY = "agent_query"
    SYSTEM_STATUS = "system_status"

class MCPRole(str, Enum):
    EVENT_MANAGER = "event_manager"
    DISCORD_ADAPTER = "discord_adapter"
    SLACK_ADAPTER = "slack_adapter"
    EXPERIENCE_COLLECTOR = "experience_collector"
    PHOTO_VIBE_CHECK = "photo_vibe_check"
    VIBE_BIT = "vibe_bit"
    SYSTEM_MONITOR = "system_monitor"

class MCPToolRequest(BaseModel):
    tool_name: str
    method: str  # GET, POST, PUT, DELETE
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MCPRequest(BaseModel):
    request_id: str
    request_type: MCPRequestType
    role: Optional[MCPRole] = None
    tool_request: Optional[MCPToolRequest] = None
    query: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    request_id: str
    success: bool
    role: Optional[MCPRole] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# RBAC Models for FastMCP 2.0 Gateway
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    EVENT_OWNER = "event_owner"

class AuthContext(BaseModel):
    user_id: str
    role: UserRole
    event_permissions: List[str] = Field(default_factory=list)  # Event IDs user owns
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RBACRule(BaseModel):
    tool_pattern: str  # Tool name pattern (supports wildcards)
    allowed_roles: List[UserRole]
    description: str

class ProxyConfig(BaseModel):
    name: str
    url: str
    transport: str = "streamable-http"
    enabled: bool = True
    health_check_path: str = "/health"
    timeout: int = 30
    tools: List[str] = Field(default_factory=list)  # Tools available from this service

# Default RBAC rules
DEFAULT_RBAC_RULES = [
    # Admin can access everything
    RBACRule(
        tool_pattern="*",
        allowed_roles=[UserRole.ADMIN],
        description="Admins have full access"
    ),
    
    # Event management - read operations for all users
    RBACRule(
        tool_pattern="get_event*",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can read event data"
    ),
    RBACRule(
        tool_pattern="list_*",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can list resources"
    ),
    RBACRule(
        tool_pattern="search_events",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can search events"
    ),
    
    # Event creation and management - event owners and admins only
    RBACRule(
        tool_pattern="create_event",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can create events"
    ),
    RBACRule(
        tool_pattern="update_event",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can update events"
    ),
    RBACRule(
        tool_pattern="delete_event",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can delete events"
    ),
    RBACRule(
        tool_pattern="get_events_by_creator",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can query events by creator"
    ),
    RBACRule(
        tool_pattern="get_event_stats",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can view event statistics"
    ),
    
    # RSVP operations - all users can manage their own RSVPs
    RBACRule(
        tool_pattern="create_rsvp",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can create RSVPs"
    ),
    RBACRule(
        tool_pattern="update_rsvp",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can update their RSVPs"
    ),
    RBACRule(
        tool_pattern="delete_rsvp",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can delete their RSVPs"
    ),
    RBACRule(
        tool_pattern="get_rsvp",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can get RSVP details"
    ),
    RBACRule(
        tool_pattern="get_user_rsvp_for_event",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can check their RSVP status for events"
    ),
    RBACRule(
        tool_pattern="get_user_rsvps",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can view their own RSVPs"
    ),
    RBACRule(
        tool_pattern="update_user_rsvp",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can update their RSVP for events"
    ),
    
    # RSVP analytics and admin operations - event owners and admins
    RBACRule(
        tool_pattern="get_event_rsvps",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can view all RSVPs for events"
    ),
    RBACRule(
        tool_pattern="get_rsvp_analytics",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can view RSVP analytics"
    ),
    RBACRule(
        tool_pattern="get_rsvp_stats",
        allowed_roles=[UserRole.ADMIN],
        description="Only admins can view global RSVP statistics"
    ),
    RBACRule(
        tool_pattern="list_events_with_rsvps",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners and admins can list events with RSVPs"
    ),
    
    # Photo submissions - all users
    RBACRule(
        tool_pattern="submit_photo*",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can submit photos"
    ),
    RBACRule(
        tool_pattern="get_photo*",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can view photos"
    ),
    
    # Photo management - event owners and admins
    RBACRule(
        tool_pattern="activate_photo*",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can manage photo collection"
    ),
    RBACRule(
        tool_pattern="deactivate_photo*",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can manage photo collection"
    ),
    RBACRule(
        tool_pattern="generate_*slideshow",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can generate slideshows"
    ),
    
    # Vibe bit operations - all users can place elements
    RBACRule(
        tool_pattern="place_element",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can place vibe elements"
    ),
    RBACRule(
        tool_pattern="get_canvas*",
        allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
        description="All users can view canvas"
    ),
    
    # Canvas management - event owners and admins
    RBACRule(
        tool_pattern="create_canvas",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can create canvases"
    ),
    RBACRule(
        tool_pattern="update_canvas*",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can update canvas settings"
    ),
    RBACRule(
        tool_pattern="activate_canvas",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can activate canvases"
    ),
    
    # Analytics - restricted access
    RBACRule(
        tool_pattern="get_*analytics",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can view detailed analytics"
    ),
    RBACRule(
        tool_pattern="get_*stats",
        allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
        description="Only event owners can view detailed stats"
    )
]