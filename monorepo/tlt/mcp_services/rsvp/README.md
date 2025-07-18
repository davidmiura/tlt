# TLT RSVP Service

A dedicated FastMCP service for managing user RSVP operations, separated from event management for better RBAC control.

## Purpose

This service handles all user-facing RSVP operations, allowing the gateway to enforce different permissions for:
- **Users**: Can create, read, update their own RSVPs
- **Event Owners**: Can view RSVP analytics and summaries for their events
- **Admins**: Full access to all RSVP operations

## Features

### 🎯 User RSVP Operations
- Create and update RSVPs with single emoji responses
- View personal RSVP history
- Get RSVP status for specific events
- Delete RSVPs when needed

### 📊 RSVP Analytics
- Event-level RSVP summaries and analytics
- Emoji breakdown and usage statistics
- Response timeline tracking
- User participation metrics

### 😀 Emoji-Based Responses
- Single emoji validation
- Unicode emoji support
- Flexible response system for LLM analysis
- No predefined status constraints

## Tools

### User Operations
- `create_rsvp(event_id, user_id, emoji, metadata?)` - Create new RSVP
- `get_rsvp(rsvp_id)` - Get RSVP by ID
- `update_rsvp(rsvp_id, emoji?, metadata?)` - Update existing RSVP
- `delete_rsvp(rsvp_id)` - Delete RSVP
- `get_user_rsvp_for_event(user_id, event_id)` - Get user's RSVP for event
- `get_user_rsvps(user_id)` - Get all RSVPs for user
- `update_user_rsvp(event_id, user_id, emoji, metadata?)` - Update/create user RSVP

### Analytics & Admin Operations
- `get_event_rsvps(event_id)` - Get all RSVPs for event
- `get_rsvp_analytics(event_id)` - Detailed RSVP analytics
- `list_events_with_rsvps()` - List events that have RSVPs
- `get_rsvp_stats()` - Overall service statistics

## Resources

- `rsvp://event/{event_id}` - RSVP summary for specific event
- `rsvp://user/{user_id}` - RSVP history for specific user  
- `rsvp://analytics/{event_id}` - Detailed analytics for event
- `rsvp://stats` - Overall service statistics
- `rsvp://events` - List of all events with RSVPs

## Data Models

### RSVPCreate
```python
{
    "event_id": "event_123",
    "user_id": "user_456", 
    "emoji": "👍",
    "metadata": {}
}
```

### RSVPResponse
```python
{
    "rsvp_id": "rsvp_789",
    "event_id": "event_123",
    "user_id": "user_456",
    "emoji": "👍",
    "response_time": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "metadata": {}
}
```

### RSVPAnalytics
```python
{
    "event_id": "event_123",
    "total_responses": 42,
    "emoji_breakdown": {"👍": 25, "❤️": 10, "🤔": 7},
    "response_timeline": [...],
    "most_popular_emoji": "👍",
    "unique_users": 42,
    "peak_response_time": "2024-01-15T18:00:00Z",
    "average_response_time": 2.5
}
```

## Usage

### Running the Service

```bash
# With stdio transport (development)
python -m mcp.rsvp.main

# With HTTP transport (production)
MCP_TRANSPORT=streamable-http PORT=8007 python -m mcp.rsvp.main

# Using fastmcp command
fastmcp run mcp/rsvp/main.py --transport streamable-http --port 8007
```

### Environment Variables

```bash
MCP_TRANSPORT=streamable-http  # or stdio
PORT=8007                      # Service port
```

### Example Usage

```python
# Create an RSVP
await call_tool("create_rsvp", {
    "event_id": "community_meetup_2024",
    "user_id": "alice_smith",
    "emoji": "🎉",
    "metadata": {"source": "mobile_app"}
})

# Update user's RSVP
await call_tool("update_user_rsvp", {
    "event_id": "community_meetup_2024", 
    "user_id": "alice_smith",
    "emoji": "❤️"
})

# Get event RSVP summary
await call_tool("get_event_rsvps", {
    "event_id": "community_meetup_2024"
})
```

## RBAC Integration

This service is designed to work with the MCP Gateway's RBAC system:

### User Permissions
- `create_rsvp`, `update_rsvp`, `delete_rsvp` (own RSVPs only)
- `get_user_rsvp_for_event`, `get_user_rsvps` (own data only)
- `update_user_rsvp` (own RSVP only)

### Event Owner Permissions  
- All user permissions
- `get_event_rsvps`, `get_rsvp_analytics` (for owned events)
- `list_events_with_rsvps`

### Admin Permissions
- All tools and operations
- `get_rsvp_stats` (service-wide statistics)

## Architecture

```
┌─────────────────┐
│   Gateway       │ ← RBAC enforcement
│   (Port 8003)   │
└─────────┬───────┘
          │
┌─────────▼───────┐
│  RSVP Service   │ ← User RSVP operations
│  (Port 8007)    │
└─────────────────┘
```

## Separation from Event Manager

The RSVP service is intentionally separated from the Event Manager to:

1. **Enable Granular RBAC**: Users can manage RSVPs without event creation permissions
2. **Service Isolation**: RSVP operations don't affect event management
3. **Scalability**: Each service can scale independently
4. **Clear Responsibilities**: Events vs RSVPs have different access patterns

## Data Flow

1. **User Creates RSVP**: Gateway → RSVP Service → Store RSVP
2. **Event Owner Views Analytics**: Gateway → RSVP Service → Aggregate data
3. **Admin Views Stats**: Gateway → RSVP Service → Global statistics

## Development

### Adding New RSVP Features

1. Add models in `models.py`
2. Implement business logic in `service.py`
3. Create tools in `tools.py` 
4. Add resources in `resources.py`
5. Update gateway proxy configuration

### Testing

```bash
# Test with development config
fastmcp run mcp/rsvp/main.py --transport stdio

# Test specific tools
echo '{"tool": "create_rsvp", "args": {...}}' | fastmcp run mcp/rsvp/main.py
```

## Security

- Single emoji validation prevents injection attacks
- User ID validation for RSVP ownership
- Metadata sanitization
- Error message sanitization to prevent information leakage