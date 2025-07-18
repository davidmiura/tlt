# Ambient Event Agent

A long-running, intelligent agent that monitors events and sends contextual messages to Discord channels using LangGraph for orchestration.

## Architecture

The agent is built using LangGraph with a reactive architecture that processes events from multiple sources:

### Components

- **`main.py`**: Process control and command-line interface
- **`agent/agent.py`**: LangGraph state machine and orchestration
- **`state/state.py`**: State definitions and data models
- **`nodes/`**: Individual processing nodes
  - `initialization.py`: Agent setup and initialization
  - `event_monitor.py`: Monitor for incoming events and timers
  - `reasoning.py`: LLM-powered decision making
  - `mcp_executor.py`: MCP tool calls and external service integration
  - `discord_interface.py`: Discord message sending and rate limiting
- **`routes/router.py`**: Graph routing logic

### Event Sources

1. **Discord Adapter**: Messages, reactions, and Discord events
2. **Timer System**: RSVP-based reminders (1 day before, day of, event time, followup)
3. **Manual Triggers**: API calls and manual events
4. **MCP Services**: Events from event manager, photo vibe check, etc.

### State Management

The agent maintains comprehensive state including:
- Current processing context and status
- Event queues and timer schedules
- Message history and conversation context
- Decision tracking and tool call history
- Event and user context caches
- Error handling and retry logic

## Usage

### Basic Usage

```bash
# Run with default settings
python agents/ambient_event_agent/main.py

# Run with debug mode
ENV=production python agents/ambient_event_agent/main.py --debug

# Run with custom agent ID
ENV=production python agents/ambient_event_agent/main.py --agent-id my_agent_001

# Limit iterations (useful for testing)
ENV=production python agents/ambient_event_agent/main.py --max-iterations 100
```

### Environment Variables

- `OPENAI_API_KEY`: Required for LLM reasoning
- `EVENT_MANAGER_URL`: Event manager MCP service URL (default: http://localhost:8004)
- `PHOTO_VIBE_CHECK_URL`: Photo service URL (default: http://localhost:8005)
- `VIBE_BIT_URL`: Vibe bit canvas URL (default: http://localhost:8006)

### Configuration

```bash
# Use configuration file
python agents/ambient_event_agent/main.py --config-file config.json
```

Example `config.json`:
```json
{
  "agent_id": "production_ambient_agent",
  "debug_mode": false,
  "sleep_interval": 3.0,
  "max_iterations": null,
  "openai_api_key": "sk-...",
  "mcp_services": {
    "event_manager": "http://localhost:8004",
    "photo_vibe_check": "http://localhost:8005",
    "vibe_bit": "http://localhost:8006"
  }
}
```

## Features

### Intelligent Messaging

- **Context-aware**: Considers event details, timing, and user activity
- **Rate-limited**: Respects Discord rate limits and avoids spam
- **Priority-based**: Urgent messages can bypass normal rate limits
- **Scheduled**: Can schedule messages for optimal timing

### Event Processing

- **Timer-based reminders**: Automatically schedules reminders based on RSVP events
- **Discord integration**: Processes Discord messages and reactions
- **MCP integration**: Interacts with all MCP services for data and actions

### Decision Making

- **LLM-powered reasoning**: Uses GPT-4 for intelligent decision making
- **Context-aware**: Considers conversation history and recent activity
- **Confidence tracking**: Tracks decision confidence for learning

### Monitoring and Observability

- **Comprehensive logging**: Detailed logs for debugging and monitoring
- **Metrics tracking**: Performance and activity metrics
- **Error handling**: Robust error handling with retry logic
- **State persistence**: Uses LangGraph checkpointing for state management

## Event Types

### Timer Events

- **1 day before**: Reminder sent 24 hours before event
- **Day of**: Reminder sent 8 hours before event start
- **Event time**: Message sent when event begins
- **Followup**: Thank you message sent 24 hours after event

### Discord Events

- **Messages**: Responds to relevant Discord messages
- **Reactions**: Processes emoji reactions on event messages
- **Thread activity**: Monitors event-related threads

### Manual Events

- **API triggers**: External systems can trigger events
- **Admin commands**: Manual triggers for testing and control

## Development

### Adding New Nodes

1. Create a new node class inheriting from `BaseNode`
2. Implement the `execute` method
3. Add the node to the graph in `agent.py`
4. Update routing logic in `routes/router.py`

### Adding New Event Types

1. Add event type to `EventTriggerType` enum in `state.py`
2. Update event monitoring in `event_monitor.py`
3. Add reasoning logic in `reasoning.py`
4. Update routing as needed

### Testing

```bash
# Run with limited iterations for testing
python agents/ambient_event_agent/main.py --debug --max-iterations 10


python agents/ambient_event_agent/main.py --debug --max-iterations 1 --config-file agents/ambient_event_agent/test_config.json

# Test with simulated events
python agents/ambient_event_agent/main.py --debug --config-file test_config.json
```

## Integration

### With Discord Adapter

The agent expects to receive events from `monorepo/adapters/discord_adapter` in the following format:

```json
{
  "trigger_type": "discord_message",
  "priority": "normal",
  "discord_context": {
    "guild_id": "123456789",
    "channel_id": "987654321",
    "user_id": "555666777",
    "message_id": "msg_123"
  },
  "data": {
    "content": "Hey, what time is the event?",
    "author": "username"
  }
}
```

### With MCP Services

The agent integrates with:
- **Event Manager**: For RSVP data and event information
- **Photo Vibe Check**: For photo submission events
- **Vibe Bit**: For canvas interaction events

## Troubleshooting

### Common Issues

1. **Agent not starting**: Check OPENAI_API_KEY is set
2. **No events processing**: Verify MCP services are running
3. **Messages not sending**: Check Discord adapter connection
4. **High memory usage**: Adjust conversation history limits in config

### Logs

Check `ambient_event_agent.log` for detailed operation logs:

```bash
tail -f ambient_event_agent.log
```

### Debug Mode

Run with `--debug` for verbose logging and state tracking.