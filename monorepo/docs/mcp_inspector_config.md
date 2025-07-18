# MCP Inspector Configuration for TLT Services

## 🔧 Correct URLs for MCP Inspector

When using MCP Inspector to test the TLT MCP services, use these **exact URLs** (note the trailing slash):

### ✅ Correct URLs:
- **Gateway**: `http://localhost:8003/mcp/`
- **Event Manager**: `http://localhost:8004/mcp/`
- **RSVP Service**: `http://localhost:8007/mcp/`

### ❌ Incorrect URLs (will cause 307 redirects):
- `http://localhost:8003/mcp` (missing trailing slash)
- `http://localhost:8004/mcp` (missing trailing slash)
- `http://localhost:8007/mcp` (missing trailing slash)

## 🚨 Why the Redirect Happens

FastMCP (and FastAPI) automatically redirects `/mcp` to `/mcp/` with a **307 Temporary Redirect**. This is normal behavior, but some MCP clients (including MCP Inspector) may not handle redirects properly.

## 🛠️ MCP Inspector Setup

1. **Open MCP Inspector**
2. **Add Server Configuration**:
   - **Name**: TLT Gateway
   - **URL**: `http://localhost:8003/mcp/`
   - **Transport**: HTTP

3. **Repeat for other services**:
   - Event Manager: `http://localhost:8004/mcp/`
   - RSVP Service: `http://localhost:8007/mcp/`

## 🧪 Test Commands

You can also test with curl:

```bash
# Test direct connection (should work)
curl -X POST http://localhost:8003/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"test","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"Test","version":"1.0.0"}}}'

# Test redirect behavior (will show 307)
curl -I http://localhost:8003/mcp
```

## 🔍 Verify Services Are Running

Before using MCP Inspector, ensure all services are running:

```bash
# Check if services are listening
lsof -i :8003 -i :8004 -i :8007

# Or test with simple HTTP requests
curl http://localhost:8003/health
curl http://localhost:8004/health  
curl http://localhost:8007/health
```

## 💡 Pro Tip

Always use the **trailing slash** (`/mcp/`) in MCP client configurations to avoid redirect issues.