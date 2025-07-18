# TLT Photo Vibe Check MCP Server

This is a FastMCP 2.0-based Model Context Protocol (MCP) server that manages photo submissions from Discord users who have RSVP'd to events. It uses LangChain and LangGraph for intelligent photo analysis, curation, and slideshow generation.

## Features

### Photo Submission System
- **RSVP Validation**: Only users with valid RSVPs can submit photos
- **Rate Limiting**: Configurable rate limits (default: 1 photo per hour per user)
- **Time Window Validation**: Photos accepted during event and up to 24 hours after (configurable)
- **Admin Controls**: Event admins can activate/deactivate, set limits, and manage settings

### Intelligent Photo Processing
- **LangGraph Workflow**: Multi-step photo processing pipeline
- **LLM Analysis**: GPT-4 Vision for content analysis and quality assessment
- **Pre-event Curation**: Admin-uploaded reference photos for relevance comparison
- **Scoring System**: Quality, relevance, and similarity scores combined into overall rating
- **Automated Approval**: Photos above threshold automatically approved for slideshow

### Slideshow Generation
- **Ranked Collection**: Photos sorted by overall score
- **Automated Curation**: Only approved photos included
- **Statistics Tracking**: Submission counts, approval rates, user participation

## MCP Tools

### Admin Tools
- `activate_photo_collection` - Activate photo collection for an event
- `deactivate_photo_collection` - Deactivate photo collection
- `update_photo_settings` - Update rate limits and time windows
- `add_pre_event_photos` - Upload reference photos for curation

### User Tools  
- `submit_photo_dm` - Submit photo from Discord DM
- `get_photo_status` - Check processing status of submitted photo
- `get_user_photo_history` - View user's submission history

### Event Tools
- `get_event_photo_summary` - Get event photo statistics
- `generate_event_slideshow` - Create slideshow from approved photos

## MCP Resources

### Configuration
- `photo_config://{event_id}` - Event photo collection settings
- `photo_stats://server` - Server-wide statistics

### Photo Data
- `photo_submissions://{event_id}` - All submissions for an event
- `photo_analysis://{photo_id}` - Detailed analysis for a specific photo
- `user_photos://{user_id}` - User's photo submission history
- `slideshow://{event_id}` - Event slideshow information

## Photo Processing Pipeline (LangGraph)

The photo processing uses a LangGraph workflow with these steps:

1. **Download Photo** - Fetch and validate image file
2. **Size & Quality Check** - Validate dimensions and technical quality
3. **Content Analysis** - LLM analysis of photo content and aesthetics
4. **Similarity Comparison** - Compare against pre-event reference photos
5. **Final Scoring** - Calculate weighted overall score

### Scoring Criteria
- **Quality Score** (30%): Technical quality, resolution, clarity
- **Relevance Score** (40%): Event-related content, appropriateness
- **Similarity Score** (30%): Matches with pre-event reference photos

### Approval Threshold
Photos with overall score ≥ 0.7 are automatically approved for slideshow inclusion.

## Installation

1. Install dependencies:
```bash
poetry install
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export EVENT_MANAGER_URL="http://localhost:8004"  # Optional
export PORT=8005  # Optional
```

3. Run the MCP server:
```bash
# For stdio transport (development)
python -m mcp.photo_vibe_check.main

# For SSE transport (production)
MCP_TRANSPORT=sse PORT=8005 python -m mcp.photo_vibe_check.main
```

## Usage Examples

### Admin Setup
```python
# Activate photo collection for an event
result = await mcp_client.call_tool("activate_photo_collection", {
    "event_id": "event_123",
    "admin_user_id": "admin_456",
    "rate_limit_hours": 1,
    "max_hours_after_event": 24,
    "event_start_time": "2024-01-15T18:00:00Z",
    "pre_event_photos": [
        "https://example.com/venue.jpg",
        "https://example.com/logo.png"
    ]
})

# Add more reference photos
result = await mcp_client.call_tool("add_pre_event_photos", {
    "event_id": "event_123", 
    "admin_user_id": "admin_456",
    "photo_urls": ["https://example.com/swag.jpg"]
})
```

### Photo Submission (from Discord Adapter)
```python
# Submit photo from Discord DM
result = await mcp_client.call_tool("submit_photo_dm", {
    "event_id": "event_123",
    "user_id": "user_789",
    "photo_url": "https://discord.com/attachments/photo.jpg",
    "metadata": {
        "source": "discord_dm",
        "message_id": "msg_123",
        "channel_id": "dm_channel_456"
    }
})
```

### Slideshow Generation
```python
# Generate slideshow from approved photos
result = await mcp_client.call_tool("generate_event_slideshow", {
    "event_id": "event_123"
})

# The result contains ranked photos ready for Discord posting
photos = result["photos"]  # List of photo URLs with scores
```

### Resource Access
```python
# Get event photo summary
summary = await mcp_client.read_resource("photo_submissions://event_123")

# Get photo analysis details
analysis = await mcp_client.read_resource("photo_analysis://photo_456")

# Get slideshow
slideshow = await mcp_client.read_resource("slideshow://event_123")
```

## Integration with Discord Adapter

The Photo Vibe Check server is designed to receive calls from the Discord Adapter when:

1. **Users send DMs with photos** - Discord bot forwards to `submit_photo_dm`
2. **Event ends** - Discord bot calls `generate_event_slideshow`
3. **Slideshow ready** - Discord bot posts photos to event thread

## Configuration Options

### Rate Limiting
- Default: 1 photo per hour per user
- Configurable by admin
- Tracks submissions per user per event

### Time Windows
- Default: Event time + 24 hours
- Configurable by admin
- Prevents submissions outside event window

### Photo Requirements
- Minimum resolution: 640x480
- Maximum file size: 10MB
- Supported formats: AVIF, JPG, JPEG, PNG, GIF, WebP

### Quality Thresholds
- **High Quality**: ≥1920x1080 resolution
- **Medium Quality**: ≥1280x720 resolution  
- **Low Quality**: ≥640x480 resolution
- **Unusable**: Below minimum requirements

## Error Handling

The service provides comprehensive error handling:
- Invalid photo formats
- Network timeouts
- API rate limits
- Missing RSVP validation
- Time window violations
- Rate limit exceeded

All errors are logged and returned with user-friendly messages.

## Security

- RSVP validation prevents unauthorized submissions
- Admin-only configuration changes
- Rate limiting prevents spam
- File size limits prevent abuse
- Content analysis for inappropriate material

## Dependencies

- **FastMCP 2.0** - MCP server framework
- **LangChain** - LLM integration and chains
- **LangGraph** - Workflow orchestration
- **OpenAI GPT-4 Vision** - Photo content analysis
- **Pillow** - Image processing
- **httpx** - HTTP client for API calls

## Environment Variables

- `OPENAI_API_KEY` - Required for photo analysis
- `EVENT_MANAGER_URL` - URL of event manager service (default: http://localhost:8004)
- `PORT` - Port for SSE transport (default: 8005)
- `MCP_TRANSPORT` - Transport type: 'stdio' or 'sse' (default: stdio)

## Architecture

The server is structured with:
- `main.py` - FastMCP server initialization
- `service.py` - Core business logic and validation
- `photo_processor.py` - LangGraph workflow for photo analysis
- `tools.py` - MCP tool definitions
- `resources.py` - MCP resource definitions
- `models.py` - Data models and types

This architecture provides a clean separation of concerns and makes the codebase maintainable and testable.