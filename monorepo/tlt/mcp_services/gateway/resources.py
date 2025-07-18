from typing import Dict, Any
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.gateway.gateway_simple import SimpleGateway

# Using loguru logger imported above

def register_resources(mcp: FastMCP, gateway: SimpleGateway):
    """Register MCP resources for the gateway service"""
    
    @mcp.resource("gateway://status")
    def get_gateway_status_resource() -> str:
        """Get comprehensive gateway status and health information"""
        try:
            result = "TLT MCP Gateway Status\n"
            result += "=" * 30 + "\n\n"
            
            result += "🌐 Gateway Information:\n"
            result += f"  Service: TLT MCP Gateway\n"
            result += f"  Version: 2.0.0\n"
            result += f"  FastMCP: 2.9+ with proxy support\n"
            result += f"  RBAC: Enabled\n\n"
            
            result += "🔌 Backend Services:\n"
            for service_name, service in gateway.backend_services.items():
                result += f"  ✅ {service['name']}\n"
                result += f"    URL: {service['url']}\n"
                result += f"    Tools: {len(service['tools'])}\n\n"
            
            result += "🔐 Casbin RBAC Configuration:\n"
            policies = gateway.rbac.get_policy()
            result += f"  Total Policies: {len(policies)}\n"
            result += f"  User Roles: admin, event_owner, user\n"
            result += f"  Role Hierarchy: admin > event_owner > user\n"
            result += f"  Policy Engine: Casbin\n\n"
            
            result += "🛠️ Gateway Tools:\n"
            gateway_tools = [
                "get_gateway_status", "get_user_permissions", 
                "get_available_tools", "get_casbin_policies",
                "add_casbin_policy", "remove_casbin_policy",
                "get_user_roles", "add_user_role", "remove_user_role"
            ]
            for tool in gateway_tools:
                result += f"  • {tool}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting gateway status: {e}")
            return f"Error retrieving gateway status: {str(e)}"
    
    @mcp.resource("gateway://services")
    def get_proxied_services_resource() -> str:
        """Get detailed information about all proxied services"""
        try:
            result = "Proxied MCP Services\n"
            result += "=" * 25 + "\n\n"
            
            for service_name, service in gateway.backend_services.items():
                result += f"📋 {service['name']}\n"
                result += f"Service ID: {service_name}\n"
                result += f"URL: {service['url']}\n"
                result += f"Status: 🟢 Active\n\n"
                
                if service['tools']:
                    result += f"Available Tools ({len(service['tools'])}):\n"
                    for tool in service['tools']:
                        result += f"  • {tool}\n"
                else:
                    result += "No tools configured\n"
                
                result += "\n" + "-" * 40 + "\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting proxied services: {e}")
            return f"Error retrieving proxied services: {str(e)}"
    
    @mcp.resource("gateway://rbac")
    def get_rbac_configuration_resource() -> str:
        """Get detailed RBAC rules and permissions"""
        try:
            result = "Casbin RBAC Configuration\n"
            result += "=" * 28 + "\n\n"
            
            result += "👥 User Roles:\n"
            result += "  • admin - Full system access (inherits all permissions)\n"
            result += "  • event_owner - Can create and manage events (inherits user permissions)\n"
            result += "  • user - Standard user permissions (RSVP operations)\n\n"
            
            result += "🔒 Casbin Policy Rules:\n"
            policies = gateway.rbac.get_policy()
            for i, policy in enumerate(policies, 1):
                if len(policy) >= 3:
                    role, resource, action = policy[0], policy[1], policy[2]
                    result += f"{i}. Role: {role}\n"
                    result += f"   Resource: {resource}\n"
                    result += f"   Action: {action}\n\n"
            
            result += "🔧 Casbin Features:\n"
            result += "  • Policy-based access control\n"
            result += "  • Role hierarchy (admin > event_owner > user)\n"
            result += "  • Resource pattern matching with keyMatch2\n"
            result += "  • Dynamic policy management\n"
            result += "  • Persistent policy storage\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting RBAC configuration: {e}")
            return f"Error retrieving RBAC configuration: {str(e)}"
    
    @mcp.resource("gateway://tools/{service_name}")
    def get_service_tools_resource(service_name: str) -> str:
        """Get tools available from a specific service"""
        try:
            if service_name not in gateway.backend_services:
                return f"Service '{service_name}' not found. Available services: {', '.join(gateway.backend_services.keys())}"
            
            service = gateway.backend_services[service_name]
            
            result = f"Tools for {service['name']}\n"
            result += "=" * (len(service['name']) + 10) + "\n\n"
            
            result += f"Service: {service['name']}\n"
            result += f"URL: {service['url']}\n"
            result += f"Status: 🟢 Active\n\n"
            
            if service['tools']:
                result += f"Available Tools ({len(service['tools'])}):\n\n"
                
                # Group tools by category
                event_tools = [t for t in service['tools'] if 'event' in t.lower()]
                rsvp_tools = [t for t in service['tools'] if 'rsvp' in t.lower()]
                photo_tools = [t for t in service['tools'] if 'photo' in t.lower()]
                canvas_tools = [t for t in service['tools'] if 'canvas' in t.lower() or 'element' in t.lower()]
                other_tools = [t for t in service['tools'] if t not in event_tools + rsvp_tools + photo_tools + canvas_tools]
                
                if event_tools:
                    result += "📅 Event Management:\n"
                    for tool in event_tools:
                        result += f"  • {tool}\n"
                    result += "\n"
                
                if rsvp_tools:
                    result += "✅ RSVP Management:\n"
                    for tool in rsvp_tools:
                        result += f"  • {tool}\n"
                    result += "\n"
                
                if photo_tools:
                    result += "📸 Photo Management:\n"
                    for tool in photo_tools:
                        result += f"  • {tool}\n"
                    result += "\n"
                
                if canvas_tools:
                    result += "🎨 Canvas Management:\n"
                    for tool in canvas_tools:
                        result += f"  • {tool}\n"
                    result += "\n"
                
                if other_tools:
                    result += "🔧 Other Tools:\n"
                    for tool in other_tools:
                        result += f"  • {tool}\n"
                    result += "\n"
            else:
                result += "No tools configured for this service\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting tools for service {service_name}: {e}")
            return f"Error retrieving tools for service {service_name}: {str(e)}"
    
    @mcp.resource("gateway://permissions/{role}")
    def get_role_permissions_resource(role: str) -> str:
        """Get permissions and allowed tools for a specific role"""
        try:
            from tlt.mcp_services.gateway.models import UserRole
            
            try:
                user_role = UserRole(role.lower())
            except ValueError:
                return f"Invalid role '{role}'. Valid roles: {', '.join([r.value for r in UserRole])}"
            
            result = f"Permissions for Role: {user_role.value.upper()}\n"
            result += "=" * (len(user_role.value) + 25) + "\n\n"
            
            # Get applicable rules
            applicable_rules = [rule for rule in gateway.rbac.rbac_rules if user_role in rule.allowed_roles]
            
            result += f"📋 Applicable RBAC Rules ({len(applicable_rules)}):\n\n"
            
            for rule in applicable_rules:
                result += f"Pattern: {rule.tool_pattern}\n"
                result += f"Description: {rule.description}\n"
                result += f"Shared with: {', '.join([r.value for r in rule.allowed_roles if r != user_role])}\n\n"
            
            # Get allowed tools by service
            result += "🔧 Allowed Tools by Service:\n\n"
            
            for service_name, service in gateway.backend_services.items():
                allowed_tools = []
                for tool in service['tools']:
                    # Check if this tool would be allowed for this role
                    from tlt.mcp_services.gateway.models import AuthContext
                    test_context = AuthContext(user_id="test", role=user_role)
                    if gateway.rbac.check_permission(tool, test_context):
                        allowed_tools.append(tool)
                
                result += f"{service['name']}:\n"
                if allowed_tools:
                    for tool in allowed_tools:
                        result += f"  ✅ {tool}\n"
                else:
                    result += "  ❌ No tools accessible\n"
                    result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting permissions for role {role}: {e}")
            return f"Error retrieving permissions for role {role}: {str(e)}"