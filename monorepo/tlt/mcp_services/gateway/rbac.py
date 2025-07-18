import fnmatch
from loguru import logger
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from tlt.mcp_services.gateway.models import UserRole, AuthContext, RBACRule, DEFAULT_RBAC_RULES

# Using loguru logger imported above

class RBACMiddleware:
    """Role-Based Access Control middleware for MCP Gateway"""
    
    def __init__(self, rbac_rules: List[RBACRule] = None):
        self.rbac_rules = rbac_rules or DEFAULT_RBAC_RULES
        self.auth_resolver: Optional[Callable[[Dict[str, Any]], AuthContext]] = None
        
    def set_auth_resolver(self, resolver: Callable[[Dict[str, Any]], AuthContext]):
        """Set the authentication context resolver function"""
        self.auth_resolver = resolver
        
    def check_permission(self, tool_name: str, auth_context: AuthContext) -> bool:
        """Check if user has permission to call the specified tool"""
        try:
            # Check each RBAC rule
            for rule in self.rbac_rules:
                if fnmatch.fnmatch(tool_name.lower(), rule.tool_pattern.lower()):
                    if auth_context.role in rule.allowed_roles:
                        logger.debug(f"Access granted for {auth_context.user_id} ({auth_context.role.value}) to call {tool_name}")
                        return True
                    else:
                        logger.warning(f"Access denied for {auth_context.user_id} ({auth_context.role.value}) to call {tool_name} - role not in allowed roles: {[r.value for r in rule.allowed_roles]}")
                        return False
            
            # If no rule matches, deny by default
            logger.warning(f"Access denied for {auth_context.user_id} ({auth_context.role.value}) to call {tool_name} - no matching RBAC rule")
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission for {tool_name}: {e}")
            return False
    
    def get_allowed_tools(self, auth_context: AuthContext) -> List[str]:
        """Get list of tools the user is allowed to call"""
        allowed_tools = []
        
        for rule in self.rbac_rules:
            if auth_context.role in rule.allowed_roles:
                allowed_tools.append(rule.tool_pattern)
                
        return allowed_tools
    
    def middleware(self, tool_name: str):
        """Decorator for MCP tool functions to enforce RBAC"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract auth context from kwargs or metadata
                auth_context = self._extract_auth_context(kwargs)
                
                if not auth_context:
                    logger.error(f"No authentication context provided for tool {tool_name}")
                    raise PermissionError("Authentication required")
                
                if not self.check_permission(tool_name, auth_context):
                    logger.error(f"Access denied for user {auth_context.user_id} to tool {tool_name}")
                    raise PermissionError(f"Access denied to tool '{tool_name}' for role '{auth_context.role.value}'")
                
                # Call the original function
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _extract_auth_context(self, kwargs: Dict[str, Any]) -> Optional[AuthContext]:
        """Extract authentication context from function kwargs"""
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
        
        # 3. Use auth resolver if set
        if self.auth_resolver:
            try:
                return self.auth_resolver(kwargs)
            except Exception as e:
                logger.error(f"Error in auth resolver: {e}")
                return None
        
        # 4. Default auth context for development/testing
        logger.warning("No auth context found, using default USER role")
        return AuthContext(
            user_id="anonymous",
            role=UserRole.USER,
            event_permissions=[],
            metadata={}
        )

def default_auth_resolver(kwargs: Dict[str, Any]) -> AuthContext:
    """Default authentication resolver - extracts from common parameter patterns"""
    user_id = kwargs.get('user_id', 'anonymous')
    
    # Determine role based on parameters and patterns
    role = UserRole.USER
    event_permissions = []
    
    # Check if user is creating/managing events
    if any(key in kwargs for key in ['admin_user_id', 'created_by']) and kwargs.get('user_id') == kwargs.get('admin_user_id'):
        role = UserRole.EVENT_OWNER
    
    # Extract event permissions from parameters
    if 'event_id' in kwargs:
        event_id = kwargs['event_id']
        # In production, you'd check database for ownership
        # For now, assume user owns events they're operating on if they have admin params
        if 'admin_user_id' in kwargs and kwargs.get('user_id') == kwargs.get('admin_user_id'):
            event_permissions = [event_id]
    
    return AuthContext(
        user_id=user_id,
        role=role,
        event_permissions=event_permissions,
        metadata=kwargs.get('metadata', {})
    )

# Global RBAC middleware instance
rbac = RBACMiddleware()
rbac.set_auth_resolver(default_auth_resolver)