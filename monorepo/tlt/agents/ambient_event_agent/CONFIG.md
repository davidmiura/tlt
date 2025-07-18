# Ambient Event Agent Configuration

This document explains the configuration options for the Ambient Event Agent and how to use the test configuration.

## Configuration Files

### test_config.json

A comprehensive test configuration that sets up the agent to work with all local MCP and adapter services:

```bash
python agents/ambient_event_agent/main.py --config-file agents/ambient_event_agent/test_config.json
```

## Configuration Sections

### Basic Agent Settings

```json
{
  "agent_id": "test_ambient_event_agent",
  "debug_mode": true,
  "sleep_interval": 2.0,
  "max_iterations": 50,
  "openai_api_key": "dummy-key-for-testing"
}
```

- **agent_id**: Unique identifier for the agent instance
- **debug_mode**: Enable verbose logging and state tracking
- **sleep_interval**: Seconds between processing cycles
- **max_iterations**: Limit iterations (null for unlimited)
- **openai_api_key**: OpenAI API key for LLM reasoning

### MCP Services

Configuration for Model Context Protocol services:

#### Event Manager (Port 8004)
- **URL**: `http://localhost:8004/mcp`
- **Tools**: Event CRUD, RSVP management, analytics
- **Purpose**: Core event management functionality

#### Photo Vibe Check (Port 8005)
- **URL**: `http://localhost:8005/mcp`
- **Tools**: Photo submission, processing, slideshow generation
- **Purpose**: Event photo management and curation

#### Vibe Bit Canvas (Port 8006)
- **URL**: `http://localhost:8006/mcp`
- **Tools**: Canvas creation, element placement, progress tracking
- **Purpose**: Collaborative canvas activities for events

### Adapter Services

#### Discord Adapter (Port 8001)
- **URL**: `http://localhost:8001`
- **Webhook**: `/events`
- **Purpose**: Discord integration for messages and events

### Agent Configuration

```json
"agent_config": {
  "max_pending_events": 100,
  "max_conversation_history": 500,
  "timer_check_interval": 30,
  "max_retry_attempts": 3,
  "message_rate_limit": 8,
  "event_processing_timeout": 120,
  "reasoning_timeout": 60,
  "mcp_call_timeout": 30
}
```

### Timer Settings

Configures automatic reminders based on event schedule:

- **1 day before**: 1440 minutes (24 hours) before event
- **Day of**: 480 minutes (8 hours) before event  
- **Event time**: At event start time (0 minutes)
- **Followup**: 1440 minutes (24 hours) after event

### Discord Settings

```json
"discord_settings": {
  "default_channel_id": "123456789012345678",
  "rate_limiting": {
    "messages_per_minute": 8,
    "burst_messages": 3,
    "priority_bypass": true
  },
  "message_formatting": {
    "use_embeds": true,
    "include_timestamps": true,
    "include_event_links": true,
    "max_message_length": 2000
  }
}
```

### Reasoning Configuration

LLM settings for intelligent decision making:

```json
"reasoning_config": {
  "llm_model": "gpt-4o-mini",
  "temperature": 0.3,
  "max_tokens": 1000,
  "decision_confidence_threshold": 0.6,
  "context_window_events": 10
}
```

### Event Triggers

Configures when the agent should respond to different events:

- **RSVP Changes**: Announce when significant RSVP changes occur
- **Photo Submissions**: Acknowledge and process photo uploads
- **Canvas Activities**: Celebrate milestones and completion
- **Event Lifecycle**: Announce creation, updates, cancellations

### Testing Configuration

```json
"testing": {
  "simulate_events": true,
  "mock_mcp_responses": false,
  "event_simulation_interval": 30,
  "dummy_event_data": {
    "event_id": "test_event_123",
    "title": "Test Community Meetup",
    "description": "A test event for agent validation",
    "start_time": "2024-01-20T18:00:00Z",
    "location": "Test Venue",
    "created_by": "test_user"
  }
}
```

## Prerequisites

Before running with test configuration, ensure all services are running:

### Start MCP Services

```bash
# Terminal 1: Event Manager
cd monorepo/mcp/event_manager
fastmcp run main.py --transport streamable-http --port 8004

# Terminal 2: Photo Vibe Check  
cd monorepo/mcp/photo_vibe_check
fastmcp run main.py --transport streamable-http --port 8005

# Terminal 3: Vibe Bit Canvas
cd monorepo/mcp/vibe_bit
fastmcp run main.py --transport streamable-http --port 8006
```

### Start Discord Adapter

```bash
# Terminal 4: Discord Adapter
cd monorepo/adapters/discord_adapter
python main.py --port 8001
```

### Run Agent with Test Config

```bash
# Terminal 5: Ambient Event Agent
cd monorepo
python agents/ambient_event_agent/main.py --config-file agents/ambient_event_agent/test_config.json
```

## Environment Variables

Set these environment variables for full functionality:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export DISCORD_TOKEN="your-discord-bot-token"
export EVENT_MANAGER_URL="http://localhost:8004"
export PHOTO_VIBE_CHECK_URL="http://localhost:8005" 
export VIBE_BIT_URL="http://localhost:8006"
export DISCORD_ADAPTER_URL="http://localhost:8001"
```

## Testing Scenarios

The test configuration supports these scenarios:

1. **Event Lifecycle Testing**
   - Create events through Event Manager
   - Agent detects and announces new events
   - Schedules automatic reminders

2. **RSVP Response Testing**
   - Submit RSVPs with different emojis
   - Agent provides RSVP summaries
   - Sends updates on significant changes

3. **Photo Collection Testing**
   - Activate photo collection for events
   - Agent acknowledges submissions
   - Generates slideshows when complete

4. **Canvas Activity Testing**
   - Create collaborative canvases
   - Agent announces milestones
   - Celebrates completion

5. **Timer and Reminder Testing**
   - Fast-forward testing with short intervals
   - Verify reminder timing and content
   - Test followup messages

## Monitoring and Debugging

### Logs

Test configuration creates detailed logs:

```bash
tail -f ambient_event_agent_test.log
```

### Metrics

Monitor agent performance:
- Event processing rate
- Decision confidence scores
- MCP call success rates
- Message delivery stats

### Debug Output

Enable debug mode for verbose output:
- State transitions
- Reasoning steps
- MCP call details
- Timer scheduling

## Troubleshooting

### Common Issues

1. **Services Not Running**
   ```bash
   # Check if MCP services are accessible
   curl http://localhost:8004/health
   curl http://localhost:8005/health
   curl http://localhost:8006/health
   ```

2. **Configuration Errors**
   ```bash
   # Validate JSON syntax
   python -m json.tool test_config.json
   ```

3. **Permission Issues**
   - Ensure Discord bot has necessary permissions
   - Check channel IDs are correct
   - Verify webhook endpoints are accessible

4. **Rate Limiting**
   - Adjust message rate limits in config
   - Monitor rate limit tracking in logs
   - Use priority messaging for urgent events

### Debug Commands

```bash
# Test with minimal iterations
python agents/ambient_event_agent/main.py \
  --config-file test_config.json \
  --max-iterations 5 \
  --debug

# Test without LLM calls (mock responses)
python agents/ambient_event_agent/main.py \
  --config-file test_config.json \
  --openai-api-key "dummy-key"
```