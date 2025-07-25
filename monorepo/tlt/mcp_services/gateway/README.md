# TLT MCP Gateway

A FastMCP 2.0+ gateway service that provides native proxying to backend MCP services with Role-Based Access Control (RBAC) middleware.

## Features

### = Native MCP Proxying
- Uses FastMCP 2.0+ `use_proxy()` for seamless MCP-to-MCP communication
- Automatic tool discovery and forwarding
- Health checking and failover support
- Configurable timeouts and transports

### = Role-Based Access Control (RBAC)
- Coarse-grain access control at the gateway level
- Three built-in user roles: `admin`, `user`, `event_owner`
- Wildcard pattern matching for tool permissions
- Fine-grain control handled by individual MCP services

### =� Middleware Support
- Authentication context extraction and validation
- Permission checking before tool execution
- Audit logging for security monitoring
- Auth context forwarding to downstream services

## Proxied Services

The gateway proxies to these backend MCP services:

### Event Manager (`localhost:8004`)
- Event CRUD operations
- RSVP management
- Event analytics
- User RSVP tracking

### Photo Vibe Check (`localhost:8005`)
- Photo submission and processing
- AI-powered photo analysis
- Slideshow generation
- Photo collection management

### Vibe Bit Canvas (`localhost:8006`)
- Collaborative canvas creation
- Element placement (emojis/colors)
- Canvas rendering and progress tracking
- User contribution analytics

## User Roles

### =Q Admin
- **Access**: Full system access to all tools
- **Use Case**: System administrators, platform managers

### =d User
- **Access**: Read operations, personal RSVPs, photo submissions, canvas participation
- **Use Case**: Event attendees, community members

### <� Event Owner
- **Access**: All user permissions + event creation/management, photo/canvas administration
- **Use Case**: Event organizers, community leaders

## RBAC Rules

The gateway enforces access control through pattern-based rules:

```python
# Examples of RBAC rules
RBACRule(
    tool_pattern="create_event",
    allowed_roles=[UserRole.ADMIN, UserRole.EVENT_OWNER],
    description="Only event owners and admins can create events"
)

RBACRule(
    tool_pattern="get_*",
    allowed_roles=[UserRole.ADMIN, UserRole.USER, UserRole.EVENT_OWNER],
    description="All users can read data"
)
```

## Usage

### Running the Gateway

```bash
# With stdio transport (development)
python -m mcp.gateway.main

# With HTTP transport (production)
MCP_TRANSPORT=streamable-http PORT=8003 python -m mcp.gateway.main

# Using fastmcp command
fastmcp run mcp/gateway/main.py --transport streamable-http --port 8003
```

### Environment Variables

```bash
# Backend service URLs
EVENT_MANAGER_URL=http://localhost:8004
PHOTO_VIBE_CHECK_URL=http://localhost:8005
VIBE_BIT_URL=http://localhost:8006

# Gateway configuration
MCP_TRANSPORT=streamable-http
PORT=8003
```

### Tool Authentication

All tools require authentication context in one of these formats:

#### 1. Direct auth_context parameter
```python
await call_tool("create_event", {
    "title": "Community Meetup",
    "auth_context": {
        "user_id": "user123",
        "role": "event_owner",
        "event_permissions": ["event_456"],
        "metadata": {}
    }
})
```

#### 2. Metadata fields
```python
await call_tool("create_rsvp", {
    "event_id": "event_123",
    "metadata": {
        "user_id": "user123",
        "role": "user"
    }
})
```

#### 3. Parameter-based (auto-detected)
```python
await call_tool("update_canvas_settings", {
    "event_id": "event_123",
    "user_id": "user123",
    "admin_user_id": "user123"  # Makes user123 an event owner for this event
})
```

## Gateway-Specific Tools

The gateway provides management tools:

### `get_gateway_status()`
Get overall gateway health and proxy status

### `get_user_permissions(user_id, role, metadata?)`
Check what tools a user can access

### `get_rbac_rules()`
View current RBAC configuration

### `get_available_tools()`
List all tools from all proxied services

## Resources

Access gateway information via MCP resources:

- `gateway://status` - Gateway health and configuration
- `gateway://services` - Detailed service information  
- `gateway://rbac` - RBAC rules and permissions
- `gateway://tools/{service_name}` - Tools for specific service
- `gateway://permissions/{role}` - Permissions for specific role

## Architecture

```
                 
   MCP Client    
         ,       
          
         �       
  TLT Gateway    
                 
               
     RBAC       � Authentication & Authorization
  Middleware   
               
                 
               
    FastMCP     � Native MCP Proxying
   Proxies     
               
         ,       
          
         �                                 
       Event        Photo       Vibe Bit   
      Manager    Vibe Check      Canvas    
       :8004        :8005         :8006    
                                           
```

## Security Features

- **Authentication Required**: All tools require valid auth context
- **Role-Based Access**: Granular permissions based on user roles
- **Audit Logging**: All access attempts are logged
- **Pattern Matching**: Flexible rule definition with wildcards
- **Context Forwarding**: Auth context passed to backend services
- **Default Deny**: Unknown tools are denied by default

## Development

### Adding New Services

1. Add proxy configuration in `gateway.py`:
```python
'new_service': ProxyConfig(
    name="New Service",
    url="http://localhost:8007",
    transport="streamable-http",
    tools=["tool1", "tool2"]
)
```

2. Add RBAC rules in `models.py`:
```python
RBACRule(
    tool_pattern="new_service_*",
    allowed_roles=[UserRole.ADMIN],
    description="New service access"
)
```

### Custom Auth Resolvers

Implement custom authentication logic:

```python
def custom_auth_resolver(kwargs: Dict[str, Any]) -> AuthContext:
    # Your custom auth logic here
    return AuthContext(...)

gateway.rbac.set_auth_resolver(custom_auth_resolver)
```

## Error Handling

The gateway provides detailed error messages for:

- **Authentication Failures**: Missing or invalid auth context
- **Authorization Failures**: Insufficient permissions for tool
- **Service Unavailable**: Backend service unreachable
- **Validation Errors**: Invalid parameters or configuration

## Monitoring

Gateway provides comprehensive monitoring through:

- Health check endpoints
- Service status monitoring  
- RBAC audit logs
- Performance metrics
- Error tracking and alerting