import os
from loguru import logger
from typing import Dict, Any, Optional, List
from pathlib import Path
import casbin

from tlt.mcp_services.gateway.models import UserRole, AuthContext

# Using loguru logger imported above

class CasbinRBACMiddleware:
    """Casbin-based Role-Based Access Control middleware for MCP Gateway"""
    
    def __init__(self, model_path: Optional[str] = None, policy_path: Optional[str] = None):
        # Set default paths relative to this file
        current_dir = Path(__file__).parent
        self.model_path = model_path or str(current_dir / "rbac_model.conf")
        self.policy_path = policy_path or str(current_dir / "rbac_policy.csv")
        
        # Initialize Casbin enforcer
        try:
            self.enforcer = casbin.Enforcer(self.model_path, self.policy_path)
            logger.info(f"Casbin RBAC initialized with model: {self.model_path}, policy: {self.policy_path}")
            
            # Load role hierarchies (optional - if you want role inheritance)
            self._setup_role_hierarchies()
            
        except Exception as e:
            logger.error(f"Failed to initialize Casbin RBAC: {e}")
            raise RuntimeError(f"RBAC initialization failed: {e}")
    
    def _setup_role_hierarchies(self):
        """Set up role inheritance hierarchies"""
        # Admin inherits all permissions
        # Event_owner inherits user permissions  
        self.enforcer.add_role_for_user("admin", "event_owner")
        self.enforcer.add_role_for_user("event_owner", "user")
        
        logger.info("Role hierarchies configured: admin > event_owner > user")
    
    def check_permission(self, tool_name: str, auth_context: AuthContext) -> bool:
        """Check if user has permission to access the specified tool"""
        try:
            # Extract service and action from tool name
            service, action = self._parse_tool_name(tool_name)
            resource = f"{service}/{tool_name}"
            
            # Determine action type based on tool name patterns
            action_type = self._determine_action_type(tool_name)
            
            # Check permission using Casbin
            user_role = auth_context.role.value
            allowed = self.enforcer.enforce(user_role, resource, action_type)
            
            if allowed:
                logger.info(f"AuthContext: {auth_context.model_dump()}")
                logger.debug(f"Access granted for {auth_context.user_id} ({user_role}) to {tool_name}")
            else:
                logger.warning(f"AuthContext: {auth_context.model_dump()}")
                logger.warning(f"Access denied for {auth_context.user_id} ({user_role}) to {tool_name}")
            
            return allowed
            
        except Exception as e:
            logger.error(f"Error checking permission for {tool_name}: {e}")
            return False
    
    def _parse_tool_name(self, tool_name: str) -> tuple[str, str]:
        """Parse tool name to extract service and action"""
        # Map tools to their respective services
        event_tools = [
            "create_event", "get_event", "update_event", "delete_event",
            "list_all_events", "get_events_by_creator", "get_events_by_status",
            "get_event_analytics", "search_events", "get_event_stats"
        ]
        
        rsvp_tools = [
            "create_rsvp", "get_rsvp", "update_rsvp", "delete_rsvp",
            "get_user_rsvp_for_event", "get_event_rsvps", "get_user_rsvps",
            "update_user_rsvp", "get_rsvp_analytics", "list_events_with_rsvps",
            "get_rsvp_stats", "process_rsvp"
        ]
        
        guild_manager_tools = [
            "register_guild", "deregister_guild", "get_guild_info",
            "list_guilds", "update_guild_settings", "get_guild_stats"
        ]
        
        photo_vibe_check_tools = [
            "submit_photo_dm", "activate_photo_collection", "deactivate_photo_collection",
            "update_photo_settings", "add_pre_event_photos", "get_photo_status",
            "get_event_photo_summary", "generate_event_slideshow", "get_user_photo_history"
        ]
        
        vibe_bit_tools = [
            "vibe_bit", "create_vibe_canvas", "activate_vibe_canvas", "deactivate_vibe_canvas",
            "update_vibe_settings", "get_vibe_canvas_image", "get_vibe_canvas_preview",
            "get_vibe_canvas_stats", "get_user_vibe_history", "get_color_palettes",
            "get_emoji_sets", "create_vibe_snapshot"
        ]
        
        gateway_tools = [
            "ping", "get_gateway_status", "get_user_permissions", "get_available_tools",
            "get_casbin_policies", "add_casbin_policy", "remove_casbin_policy",
            "get_user_roles", "add_user_role", "remove_user_role"
        ]
        
        if tool_name in event_tools:
            return "event_manager", tool_name
        elif tool_name in rsvp_tools:
            return "rsvp", tool_name
        elif tool_name in guild_manager_tools:
            return "guild_manager", tool_name
        elif tool_name in photo_vibe_check_tools:
            return "photo_vibe_check", tool_name
        elif tool_name in vibe_bit_tools:
            return "vibe_bit", tool_name
        elif tool_name in gateway_tools:
            return "gateway", tool_name
        else:
            # Default to gateway for unknown tools
            return "gateway", tool_name
    
    def _determine_action_type(self, tool_name: str) -> str:
        """Determine the action type (read/write/*) based on tool name"""
        # Read operations
        read_patterns = [
            "get_", "list_", "search_", "view_", "show_", "fetch_", "retrieve_"
        ]
        
        # Write operations  
        write_patterns = [
            "create_", "update_", "delete_", "add_", "remove_", "modify_", 
            "set_", "activate_", "deactivate_", "submit_", "place_"
        ]
        
        tool_lower = tool_name.lower()
        
        for pattern in read_patterns:
            if tool_lower.startswith(pattern):
                return "read"
        
        for pattern in write_patterns:
            if tool_lower.startswith(pattern):
                return "write"
        
        # Default to read for safety
        return "read"
    
    def add_policy(self, role: str, resource: str, action: str) -> bool:
        """Add a new policy rule"""
        try:
            success = self.enforcer.add_policy(role, resource, action)
            if success:
                logger.info(f"Added policy: {role} can {action} on {resource}")
            return success
        except Exception as e:
            logger.error(f"Failed to add policy {role}, {resource}, {action}: {e}")
            return False
    
    def remove_policy(self, role: str, resource: str, action: str) -> bool:
        """Remove a policy rule"""
        try:
            success = self.enforcer.remove_policy(role, resource, action)
            if success:
                logger.info(f"Removed policy: {role} can {action} on {resource}")
            return success
        except Exception as e:
            logger.error(f"Failed to remove policy {role}, {resource}, {action}: {e}")
            return False
    
    def get_permissions_for_user(self, role: str) -> List[List[str]]:
        """Get all permissions for a user/role"""
        try:
            return self.enforcer.get_permissions_for_user(role)
        except Exception as e:
            logger.error(f"Failed to get permissions for {role}: {e}")
            return []
    
    def get_roles_for_user(self, user: str) -> List[str]:
        """Get all roles for a user"""
        try:
            return self.enforcer.get_roles_for_user(user)
        except Exception as e:
            logger.error(f"Failed to get roles for {user}: {e}")
            return []
    
    def get_users_for_role(self, role: str) -> List[str]:
        """Get all users with a specific role"""
        try:
            return self.enforcer.get_users_for_role(role)
        except Exception as e:
            logger.error(f"Failed to get users for role {role}: {e}")
            return []
    
    def add_role_for_user(self, user: str, role: str) -> bool:
        """Add a role to a user"""
        try:
            success = self.enforcer.add_role_for_user(user, role)
            if success:
                logger.info(f"Added role {role} to user {user}")
            return success
        except Exception as e:
            logger.error(f"Failed to add role {role} to user {user}: {e}")
            return False
    
    def delete_role_for_user(self, user: str, role: str) -> bool:
        """Remove a role from a user"""
        try:
            success = self.enforcer.delete_role_for_user(user, role)
            if success:
                logger.info(f"Removed role {role} from user {user}")
            return success
        except Exception as e:
            logger.error(f"Failed to remove role {role} from user {user}: {e}")
            return False
    
    def get_policy(self) -> List[List[str]]:
        """Get all policy rules"""
        try:
            return self.enforcer.get_policy()
        except Exception as e:
            logger.error(f"Failed to get policy: {e}")
            return []
    
    def save_policy(self) -> bool:
        """Save current policy to file"""
        try:
            return self.enforcer.save_policy()
        except Exception as e:
            logger.error(f"Failed to save policy: {e}")
            return False
    
    def load_policy(self) -> bool:
        """Reload policy from file"""
        try:
            return self.enforcer.load_policy()
        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            return False
    
    def get_allowed_tools(self, auth_context: AuthContext) -> List[str]:
        """Get list of tool patterns the user is allowed to access"""
        allowed_tools = []
        role = auth_context.role.value
        
        # Get all permissions for this role
        permissions = self.get_permissions_for_user(role)
        
        # Extract tool patterns from permissions
        for perm in permissions:
            if len(perm) >= 2:
                resource = perm[1]
                # Extract tool name from resource path
                if "/" in resource:
                    tool_name = resource.split("/")[-1]
                    if tool_name not in allowed_tools:
                        allowed_tools.append(tool_name)
                else:
                    if resource not in allowed_tools:
                        allowed_tools.append(resource)
        
        return allowed_tools
    
    def _extract_auth_context(self, kwargs: Dict[str, Any]) -> Optional[AuthContext]:
        """Extract authentication context from function kwargs (compatibility method)"""
        # Look for auth context in different places
        
        # 1. Direct auth_context parameter
        if 'auth_context' in kwargs:
            return kwargs['auth_context']
        
        # 2. In metadata
        if 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
            metadata = kwargs['metadata']
            if 'auth_context' in metadata:
                return metadata['auth_context']
            
            # Try to construct from individual fields
            if 'user_id' in metadata and 'role' in metadata:
                try:
                    role = UserRole(metadata['role']) if isinstance(metadata['role'], str) else metadata['role']
                    return AuthContext(
                        user_id=metadata['user_id'],
                        role=role,
                        event_permissions=metadata.get('event_permissions', []),
                        metadata=metadata.get('user_metadata', {})
                    )
                except ValueError as e:
                    logger.error(f"Invalid role in metadata: {e}")
                    return None
        
        # 3. Construct from direct parameters
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            role = UserRole.USER  # Default role
            
            # Try to determine role from parameters
            if 'role' in kwargs:
                try:
                    role = UserRole(kwargs['role']) if isinstance(kwargs['role'], str) else kwargs['role']
                except ValueError:
                    role = UserRole.USER
            
            return AuthContext(
                user_id=user_id,
                role=role,
                event_permissions=[],
                metadata={}
            )
        
        # 4. Default auth context for development/testing
        logger.warning("No auth context found, using default USER role")
        return AuthContext(
            user_id="anonymous",
            role=UserRole.USER,
            event_permissions=[],
            metadata={}
        )

# Global Casbin RBAC middleware instance
casbin_rbac = CasbinRBACMiddleware()