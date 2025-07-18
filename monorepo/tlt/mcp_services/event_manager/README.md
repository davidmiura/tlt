# TLT Event Manager MCP Server

This is a FastMCP 2.0-based Model Context Protocol (MCP) server that handles RSVP state management and event analytics for the TLT event management system.

## Features

### MCP Tools
- `create_rsvp` - Create a new RSVP for an event
- `update_rsvp` - Update an existing RSVP
- `delete_rsvp` - Delete an RSVP
- `get_rsvp` - Get details of a specific RSVP
- `update_user_rsvp` - Update or create RSVP for a user in an event
- `get_event_rsvps` - Get all RSVPs for an event with summary statistics
- `get_event_analytics` - Get detailed analytics for an event
- `get_user_rsvps` - Get all RSVPs for a specific user
- `list_events` - List all events that have RSVPs

### MCP Resources
- `events://list` - List of all events with RSVPs
- `event://{event_id}/summary` - RSVP summary for a specific event
- `event://{event_id}/analytics` - Detailed analytics for a specific event
- `user://{user_id}/rsvps` - All RSVPs for a specific user
- `rsvp://{rsvp_id}` - Detailed information about a specific RSVP
- `stats://server` - Overall server statistics

## RSVP Status Types
- `attending` - User will attend the event
- `not_attending` - User will not attend the event
- `maybe` - User might attend the event
- `tentative` - User is tentatively planning to attend

## Installation

1. Install dependencies:
```bash
poetry install
```

2. Run the MCP server:
```bash
# For stdio transport (development)
python -m mcp.event_manager.main

# For local (development)
fastmcp run mcp/photo_vibe_check/main.py --transport streamable-http --port 8004

# For SSE transport (production)
MCP_TRANSPORT=sse PORT=8004 python -m mcp.event_manager.main
```

## Usage Examples

### Using MCP Tools

```python
# Create an RSVP
result = await mcp_client.call_tool("create_rsvp", {
    "event_id": "event_123",
    "user_id": "user_456", 
    "status": "attending",
    "metadata": {"dietary_restrictions": "vegetarian"}
})

# Get event summary
result = await mcp_client.call_tool("get_event_rsvps", {
    "event_id": "event_123"
})

# Update user RSVP
result = await mcp_client.call_tool("update_user_rsvp", {
    "event_id": "event_123",
    "user_id": "user_456",
    "status": "maybe"
})
```

### Using MCP Resources

```python
# Get event summary
summary = await mcp_client.read_resource("event://event_123/summary")

# Get user's RSVPs
user_rsvps = await mcp_client.read_resource("user://user_456/rsvps")

# Get server statistics
stats = await mcp_client.read_resource("stats://server")
```

## Integration with TLT Gateway

The Event Manager MCP server is designed to work with the TLT MCP Gateway, which routes requests based on role identification. The gateway automatically forwards RSVP-related requests to this service.

## Data Models

### RSVP
- `rsvp_id` - Unique identifier for the RSVP
- `event_id` - ID of the event
- `user_id` - ID of the user
- `status` - RSVP status (attending, not_attending, maybe, tentative)
- `response_time` - When the user responded
- `created_at` - When the RSVP was created
- `updated_at` - When the RSVP was last updated
- `metadata` - Additional data (dietary restrictions, notes, etc.)

### Event RSVP Summary
- Total responses count
- Count by status (attending, not_attending, maybe, tentative)
- Response rate
- Last updated timestamp
- List of all RSVPs

### Event Analytics
- Response breakdown by status
- Response timeline (hourly buckets)
- Peak response time
- Average response time
- Metadata with analysis timestamp

## Environment Variables

- `PORT` - Port for SSE transport (default: 8004)
- `MCP_TRANSPORT` - Transport type: 'stdio' or 'sse' (default: stdio)

## Architecture

The server is structured with:
- `main.py` - FastMCP server initialization and routing
- `service.py` - Business logic for RSVP management
- `tools.py` - MCP tool definitions
- `resources.py` - MCP resource definitions
- `models.py` - Data models and types

This architecture provides a clean separation of concerns and makes the codebase maintainable and testable.