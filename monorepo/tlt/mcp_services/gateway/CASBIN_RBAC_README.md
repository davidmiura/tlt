# Casbin RBAC Implementation for MCP Gateway

This document describes the Casbin-based Role-Based Access Control (RBAC) system implemented in the MCP Gateway.

## Overview

The MCP Gateway now uses [Casbin](https://casbin.org/) for fine-grained, policy-based access control. Casbin provides a powerful and flexible authorization framework that supports various access control models.

## Architecture

### Components

1. **Casbin Model** (`rbac_model.conf`) - Defines the RBAC model structure
2. **Casbin Policies** (`rbac_policy.csv`) - Contains the actual permission rules
3. **CasbinRBACMiddleware** (`casbin_rbac.py`) - Python wrapper for Casbin integration
4. **Gateway Integration** (`gateway_simple.py`) - Integration with FastMCP tools

### RBAC Model Configuration

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && keyMatch2(r.obj, p.obj) && r.act == p.act
```

### Role Hierarchy

The system implements a three-tier role hierarchy:

```
admin > event_owner > user
```

- **admin**: Full system access (inherits all permissions)
- **event_owner**: Can create and manage events (inherits user permissions)
- **user**: Standard user permissions (RSVP operations only)

## Permissions

### Admin Role
- Full access to all resources (`*`, `*`)
- Can manage Casbin policies
- Can manage user roles
- Access to all gateway management tools

### Event Owner Role
- **Event Management**: Create, update, delete, read events
- **RSVP Analytics**: Read-only access to RSVP data and analytics
- **Gateway**: Read-only access to gateway status and tools

### User Role
- **Event Access**: Read-only access to events (get, list, search)
- **RSVP Management**: Full CRUD operations on RSVPs
- **Gateway**: Basic access to status and available tools

## Tool-to-Service Mapping

### Event Manager Service (`event_manager/*`)
- `create_event`, `update_event`, `delete_event` - Event Owner+ only
- `get_event`, `list_all_events`, `search_events` - All roles

### RSVP Service (`rsvp/*`)
- All RSVP operations - User+ roles
- Analytics operations - Event Owner+ for analysis

### Gateway Service (`gateway/*`)
- Management tools (`get_casbin_policies`, `add_casbin_policy`) - Admin only
- Status tools (`get_gateway_status`, `get_available_tools`) - All roles

## API Endpoints

### Casbin Management Tools

#### `get_casbin_policies()`
Returns all current Casbin policies.
- **Access**: Admin only
- **Returns**: List of all policy rules with role, resource, and action

#### `add_casbin_policy(role, resource, action, user_id?)`
Adds a new policy rule to the system.
- **Access**: Admin only
- **Parameters**: 
  - `role`: Role name (admin, event_owner, user)
  - `resource`: Resource pattern (e.g., `event_manager/create_event`)
  - `action`: Action type (read, write, *)
  - `user_id`: Optional admin user ID for verification

#### `remove_casbin_policy(role, resource, action, user_id?)`
Removes a policy rule from the system.
- **Access**: Admin only
- **Parameters**: Same as add_casbin_policy

#### `get_user_roles(user_id)`
Gets all roles assigned to a specific user.
- **Access**: Admin only
- **Returns**: User roles and associated permissions

#### `add_user_role(user_id, role, admin_user_id?)`
Assigns a role to a user.
- **Access**: Admin only
- **Parameters**:
  - `user_id`: Target user ID
  - `role`: Role to assign
  - `admin_user_id`: Admin performing the operation

#### `remove_user_role(user_id, role, admin_user_id?)`
Removes a role from a user.
- **Access**: Admin only
- **Parameters**: Same as add_user_role

## Permission Checking

The system uses a two-step permission checking process:

1. **Tool Mapping**: Maps tool names to service/resource patterns
2. **Action Detection**: Determines action type (read/write) based on tool name patterns

### Tool Name Patterns

- **Read Operations**: `get_*`, `list_*`, `search_*`, `view_*`
- **Write Operations**: `create_*`, `update_*`, `delete_*`, `add_*`, `remove_*`

### Resource Pattern Matching

Casbin uses `keyMatch2` for flexible pattern matching:
- `event_manager/*` matches all event manager tools
- `rsvp/get_*` matches all RSVP read operations
- `gateway/add_*` matches all gateway creation operations

## Configuration Files

### Policy File (`rbac_policy.csv`)
Contains policy rules in format: `p, role, resource, action`

Example policies:
```csv
p, admin, *, *
p, event_owner, event_manager/create_event, write
p, user, rsvp/create_rsvp, write
p, user, event_manager/get_event, read
```

### Model File (`rbac_model.conf`)
Defines the RBAC structure and matching logic.

## Testing

Run the test suite to verify RBAC functionality:

```bash
cd mcp/gateway
poetry run python test_casbin.py
```

The test script validates:
- Permission enforcement for different roles
- Tool access patterns
- Role hierarchy inheritance
- Policy rule validation

## Benefits of Casbin Implementation

1. **Flexibility**: Easy to modify permissions without code changes
2. **Scalability**: Supports complex permission models
3. **Auditability**: Clear policy files for compliance
4. **Performance**: Efficient pattern matching and caching
5. **Standards-Based**: Uses established RBAC principles
6. **Dynamic Management**: Runtime policy updates via API

## Usage Examples

### Check User Permissions
```python
from casbin_rbac import CasbinRBACMiddleware
from models import AuthContext, UserRole

rbac = CasbinRBACMiddleware()
user_context = AuthContext(user_id="user123", role=UserRole.USER)
can_create_event = rbac.check_permission("create_event", user_context)
```

### Add Dynamic Policy
```python
# Add policy allowing event_owner to delete RSVPs
rbac.add_policy("event_owner", "rsvp/delete_rsvp", "write")
rbac.save_policy()
```

### Get User's Allowed Tools
```python
allowed_tools = rbac.get_allowed_tools(user_context)
print(f"User can access: {allowed_tools}")
```

## Migration from Previous RBAC

The Casbin implementation replaces the previous pattern-based RBAC system with:
- More granular control
- Better performance
- Easier maintenance
- Standards compliance
- Dynamic policy management

All existing functionality is preserved while adding new capabilities for policy management and role administration.