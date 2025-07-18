# MCP Transport Configuration

This document describes the default transport configuration for all MCP services and clients in the TLT monorepo.

## Default Transport: Streamable HTTP

All MCP services and clients now use `streamable-http` as the default transport for production readiness and better performance.

## Updated Services

### MCP Servers

All MCP servers have been updated to use `streamable-http` as the default transport:

#### 1. Gateway Service (`mcp/gateway/main.py`)
- **Port**: 8003
- **Default Transport**: `streamable-http`
- **Environment Override**: `MCP_TRANSPORT`
- **URL**: `http://localhost:8003/mcp/`

#### 2. Event Manager Service (`mcp/event_manager/main.py`)
- **Port**: 8004
- **Default Transport**: `streamable-http`
- **Environment Override**: `MCP_TRANSPORT`
- **URL**: `http://localhost:8004/mcp/`

#### 3. RSVP Service (`mcp/rsvp/main.py`)
- **Port**: 8007
- **Default Transport**: `streamable-http`
- **Environment Override**: `MCP_TRANSPORT`
- **URL**: `http://localhost:8007/mcp/`

#### 4. Photo Vibe Check Service (`mcp/photo_vibe_check/main.py`)
- **Port**: 8005
- **Default Transport**: `streamable-http`
- **Environment Override**: `MCP_TRANSPORT`
- **URL**: `http://localhost:8005/mcp/`

#### 5. Vibe Bit Service (`mcp/vibe_bit/main.py`)
- **Port**: 8006
- **Default Transport**: `streamable-http`
- **Environment Override**: `MCP_TRANSPORT`
- **URL**: `http://localhost:8006/mcp/`

### MCP Clients

#### 1. Ambient Event Agent (`agents/ambient_event_agent/nodes/mcp_executor.py`)
- **Updated to use**: MCP Gateway with streamable-http
- **Gateway URL**: `http://localhost:8003/mcp/`
- **Environment Override**: `MCP_GATEWAY_URL`
- **Features**:
  - Session management with `mcp-session-id` headers
  - SSE response parsing
  - Fallback to direct service calls

## Configuration

### Environment Variables

Set these environment variables to override default behavior:

```bash
# Override default transport for any service
export MCP_TRANSPORT=stdio  # Use stdio instead of streamable-http

# Override gateway URL for clients
export MCP_GATEWAY_URL=http://localhost:8003/mcp/

# Service-specific ports
export PORT=8003  # Gateway
export PORT=8004  # Event Manager
export PORT=8005  # Photo Vibe Check
export PORT=8006  # Vibe Bit
export PORT=8007  # RSVP
```

### Starting Services

#### Development (stdio transport)
```bash
# Use stdio for development/debugging
export MCP_TRANSPORT=stdio
poetry run fastmcp run mcp/gateway/main.py
```

#### Production (streamable-http transport - default)
```bash
# Services start with streamable-http by default
poetry run python mcp/gateway/main.py
poetry run python mcp/event_manager/main.py
poetry run python mcp/rsvp/main.py
poetry run python mcp/photo_vibe_check/main.py
poetry run python mcp/vibe_bit/main.py
```

#### Using FastMCP CLI
```bash
# Gateway
poetry run fastmcp run mcp/gateway/main.py --transport streamable-http --port 8003

# Event Manager  
poetry run fastmcp run mcp/event_manager/main.py --transport streamable-http --port 8004

# RSVP Service
poetry run fastmcp run mcp/rsvp/main.py --transport streamable-http --port 8007

# Photo Vibe Check
poetry run fastmcp run mcp/photo_vibe_check/main.py --transport streamable-http --port 8005

# Vibe Bit
poetry run fastmcp run mcp/vibe_bit/main.py --transport streamable-http --port 8006
```

## Service URLs

When services are running with streamable-http transport:

| Service | URL | Description |
|---------|-----|-------------|
| Gateway | `http://localhost:8003/mcp/` | Main gateway with RBAC |
| Event Manager | `http://localhost:8004/mcp/` | Event management operations |
| RSVP Service | `http://localhost:8007/mcp/` | RSVP operations |
| Photo Vibe Check | `http://localhost:8005/mcp/` | Photo processing |
| Vibe Bit | `http://localhost:8006/mcp/` | Canvas management |

## Client Configuration

### Using MCP Gateway (Recommended)

Clients should connect to the gateway for centralized access with RBAC:

```python
# Example client code
import httpx
import json

async def call_mcp_tool(tool_name: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        # Initialize session
        init_response = await client.post(
            "http://localhost:8003/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": "init",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "MyClient", "version": "1.0.0"}
                }
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        session_id = init_response.headers.get("mcp-session-id")
        
        # Call tool
        tool_response = await client.post(
            "http://localhost:8003/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": "tool_call",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments}
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            }
        )
        
        # Parse SSE response
        lines = tool_response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                return json.loads(line[6:])
```

## Benefits of Streamable HTTP

1. **Production Ready**: HTTP-based transport suitable for deployment
2. **Better Performance**: More efficient than stdio for network communication
3. **Session Management**: Persistent connections with session IDs
4. **Scalability**: Can handle multiple concurrent clients
5. **Monitoring**: Standard HTTP status codes and headers
6. **Load Balancing**: Compatible with standard HTTP load balancers
7. **Security**: Can be secured with HTTPS and authentication

## Migration Notes

- **Backward Compatibility**: All services can still use `stdio` transport if needed via `MCP_TRANSPORT=stdio`
- **Fallback Support**: Ambient agent has fallback to direct service calls if gateway is unavailable
- **Testing**: All test suites updated to use streamable-http
- **Docker Ready**: HTTP transport works better in containerized environments

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8003-8007 are available
2. **Session Issues**: Check `mcp-session-id` header is being passed
3. **SSE Parsing**: Ensure responses are parsed as Server-Sent Events
4. **CORS**: Add appropriate CORS headers for web clients

### Health Checks

Check service health:
```bash
curl -i http://localhost:8003/mcp/
curl -i http://localhost:8004/mcp/
curl -i http://localhost:8007/mcp/
```

### Logs

Check service logs for transport configuration:
```bash
# Should show "Starting ... with streamable-http transport"
poetry run python mcp/gateway/main.py
```