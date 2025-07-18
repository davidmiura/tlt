# TLT Monorepo - Claude Code Development Guide

## Project Overview

**TLT** is a microservices-based monorepo application that combines Python backend services with a Next.js frontend dashboard. The system is designed as a containerized application using Docker and managed by supervisord for process orchestration.

### Architecture Summary

The monorepo consists of:
- **2 Adapter Services** (Python/FastAPI): Discord and Slack adapters for chat platform integration
- **2 MCP Services** (Python): Gateway and Event Manager for core business logic
- **1 Frontend Dashboard** (Next.js/TypeScript): Web interface for monitoring and management
- **1 Reverse Proxy** (Caddy): Load balancing and HTTPS termination

## Directory Structure

```
monorepo/tlt/
├── adapters/
│   ├── discord_adapter/        # Discord bot and API endpoints
│   │   ├── main.py            # FastAPI app + Discord bot runner
│   │   ├── bot_manager.py     # Discord bot implementation
│   │   ├── health.py          # Health check endpoints
│   │   ├── event.py           # Event handling routes
│   │   ├── rsvp.py           # RSVP management routes
│   │   ├── reminder.py       # Reminder system routes
│   │   ├── experience_manager.py # Experience tracking routes
│   │   └── Caddyfile         # Caddy reverse proxy config
│   └── slack_adapter/         # Slack integration (minimal implementation)
│       └── main.py           # Empty placeholder
├── mcp_services/              # Model Context Protocol services
│   ├── gateway/              # FastAPI REST Gateway service
│   │   ├── main.py          # FastAPI gateway server
│   │   ├── gateway.py       # Core gateway logic
│   │   ├── router.py        # Role-based routing
│   │   ├── routes.py        # FastAPI route definitions
│   │   └── models.py        # MCP protocol models
│   ├── event_manager/        # FastMCP 2.0 Event management service
│   │   ├── main.py          # FastMCP server
│   │   ├── service.py       # Business logic
│   │   ├── tools.py         # MCP tools
│   │   ├── resources.py     # MCP resources
│   │   └── models.py        # Data models
│   ├── photo_vibe_check/     # FastMCP 2.0 AI photo analysis service
│   │   ├── main.py          # FastMCP server
│   │   ├── service.py       # Business logic
│   │   ├── photo_processor.py # LangGraph AI workflow
│   │   ├── tools.py         # MCP tools
│   │   └── models.py        # Data models
│   └── vibe_bit/             # FastMCP 2.0 Collaborative canvas service
│       ├── main.py          # FastMCP server
│       ├── service.py       # Business logic
│       ├── canvas_renderer.py # PIL image rendering
│       ├── tools.py         # MCP tools
│       ├── resources.py     # MCP resources
│       └── models.py        # Data models
├── nextjs_app/
│   ├── dashboard/            # Next.js dashboard application
│   │   ├── src/app/         # App router structure
│   │   ├── package.json     # Dashboard dependencies
│   │   └── tsconfig.json    # TypeScript configuration
│   └── package.json         # Root Next.js package file
├── pyproject.toml           # Python dependencies (Poetry)
├── poetry.lock             # Locked Python dependencies
├── tests/                  # Organized test suite
│   ├── test_environment.py     # Environment and dependency tests
│   ├── test_service_imports.py # Service import validation tests
│   ├── test_service_health.py  # Health endpoint tests
│   ├── test_client_connections.py # Client connection tests
│   ├── run_all_tests.py        # Master test runner
│   └── [legacy test files]     # Migrated test_*.py scripts
├── logs/                   # Centralized log files
│   ├── tlt_service.log         # TLT Service logs
│   ├── discord_adapter.log     # Discord Adapter logs
│   ├── mcp_gateway.log         # MCP Gateway logs
│   ├── event_manager.log       # Event Manager logs
│   ├── photo_vibe_check.log    # Photo Vibe Check logs
│   ├── vibe_bit.log           # Vibe Bit logs
│   ├── rsvp_service.log       # RSVP Service logs
│   ├── guild_manager.log      # Guild Manager logs
│   └── ambient_event_agent.log # Ambient Event Agent logs
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile             # Multi-stage build configuration
├── supervisord.conf       # Process management configuration
├── fly.toml              # Fly.io deployment configuration
└── README.md             # Setup and installation guide
```

## Service Architecture

### Port Allocation
- **3100**: Next.js Dashboard
- **8001**: Discord Adapter (FastAPI + Discord Bot)
- **8002**: Slack Adapter (FastAPI)
- **8003**: MCP Gateway (FastAPI REST server)
- **8004**: Event Manager (FastMCP 2.0 server)
- **8005**: Photo Vibe Check (FastMCP 2.0 server)
- **8006**: Vibe Bit (FastMCP 2.0 server)
- **8007**: RSVP Service (FastMCP 2.0 server)
- **8008**: TLT Service (FastAPI + Ambient Event Agent)
- **8009**: Guild Manager (FastMCP)
- **80/443**: Caddy reverse proxy

### Service Communication
- Services are designed to communicate via HTTP APIs
- Caddy acts as reverse proxy and HTTPS termination
- supervisord manages all processes in the container
- Health checks are implemented for monitoring

## Technology Stack

### Backend (Python)
- **Framework**: FastAPI for REST APIs, FastMCP 2.0 for MCP servers
- **Chat Integration**: discord.py for Discord bot functionality
- **AI Integration**: LangChain, LangGraph, and OpenAI for AI workflows
- **Image Processing**: Pillow (PIL) for canvas rendering and image manipulation
- **Environment Management**: python-dotenv for configuration
- **ASGI Server**: uvicorn for FastAPI applications
- **Dependency Management**: Poetry (all commands from monorepo root)
- **MCP Protocol**: Model Context Protocol for tool and agent communication

### Frontend (Next.js)
- **Framework**: Next.js 15.3.3 with App Router
- **Runtime**: React 19.0.0
- **Styling**: Tailwind CSS 4.0
- **Language**: TypeScript 5.x
- **Port**: 3100 (custom port for development)

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Process Management**: supervisord
- **Reverse Proxy**: Caddy 2
- **Deployment**: Fly.io ready
- **Base OS**: Alpine Linux (caddy:2-alpine)

## Development Commands

### Environment Setup
```bash
# Install prerequisites
brew install pipx
pipx ensurepath
sudo pipx ensurepath --global
pipx install poetry
brew install virtualenv pyenv-virtualenv

# Python environment setup
pyenv install 3.12.10
pyenv local 3.12.10
eval $(poetry env activate)
poetry install --only main --no-root
poetry env list
poetry env info
```

### Development Workflow

#### Python Services Development

**IMPORTANT**: All Python commands must be run within the Poetry virtual environment. Use `poetry run` prefix for all commands to ensure proper environment setup.

```bash
# Install dependencies (from monorepo root)
poetry install --only main --no-root

# ALWAYS use 'poetry run' prefix for all Python commands
# This ensures proper virtual environment and dependency management

# Discord Adapter (FastAPI + Discord Bot)
poetry run python -m tlt.adapters.discord_adapter.main  # Runs on port 8001

# Slack Adapter (FastAPI)
poetry run python -m tlt.adapters.slack_adapter.main  # Runs on port 8002

# MCP Gateway (FastAPI REST server)
poetry run python -m tlt.mcp.gateway.main  # Runs on port 8003

# MCP Event Manager (FastMCP 2.0 server)
poetry run python -m tlt.mcp.event_manager.main  # Runs on port 8004

# MCP Photo Vibe Check (FastMCP 2.0 server)
poetry run python -m tlt.mcp.photo_vibe_check.main  # Runs on port 8005

# MCP Vibe Bit (FastMCP 2.0 server)
poetry run python -m tlt.mcp.vibe_bit.main  # Runs on port 8006

# MCP RSVP Service (FastMCP 2.0 server)
poetry run python -m tlt.mcp.rsvp.main  # Runs on port 8007

# TLT Service (FastAPI + Ambient Event Agent)
poetry run python -m tlt.services.tlt_service.main  # Runs on port 8008

# Alternative: Use fastmcp dev server for FastMCP services
poetry run fastmcp run tlt/mcp/event_manager/main.py:main
poetry run fastmcp run tlt.mcp.photo_vibe_check.main:main
poetry run fastmcp run tlt.mcp.vibe_bit.main:main
```

#### Testing Services
**IMPORTANT**: All testing commands must use Poetry virtual environment.

The TLT project includes an organized test suite under `tests/` directory:

```bash
# Run comprehensive test suite (recommended)
poetry run python tlt/tests/run_all_tests.py

# Run individual test categories
poetry run python tlt/tests/test_environment.py      # Environment and dependencies
poetry run python tlt/tests/test_service_imports.py  # Service import validation
poetry run python tlt/tests/test_service_health.py   # Health endpoint checks
poetry run python tlt/tests/test_client_connections.py # Client connection tests

# Run legacy/specific tests
poetry run python tlt/tests/test_agent_flow.py
poetry run python tlt/tests/test_discord_integration.py

# Run with pytest framework
poetry run python -m pytest tlt/tests/                # All tests
poetry run python -m pytest tlt/tests/test_service_health.py -v  # Specific test
```

**Test Categories:**
- **Environment Tests**: Verify Poetry setup, dependencies, and project structure
- **Import Tests**: Validate Python module imports for all services
- **Health Tests**: Check service availability (requires running services)
- **Connection Tests**: Test inter-service communication (requires running services)

See `tests/README.md` for detailed documentation.

#### Environment Variable Setup
Ensure proper environment variables are set before running services:

```bash
# Create .env file for development
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
DISCORD_TOKEN=your_discord_token_here
ENV=development
EOF

# For production, use .env.production
cat > .env.production << EOF
OPENAI_API_KEY=your_openai_api_key_here
DISCORD_TOKEN=your_discord_token_here
ENV=production
EOF
```

#### Next.js Dashboard Development
```bash
cd nextjs_app/dashboard

# Install dependencies
npm install

# Development server (with Turbopack)
npm run dev  # Runs on port 3100

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

### Docker Development

#### Local Docker Build
```bash
# Clean up Docker resources
docker system df
docker image prune -f
docker container prune -f

# Build for local development
docker build -t tlt/latest .

# Build for production (linux/amd64)
docker build --platform linux/amd64 -t tlt/latest .

# Run container
docker run tlt:latest

# Interactive debugging
docker run -it --entrypoint sh tlt:latest
```

#### Docker Compose
```bash
# Start all services
docker-compose up

# Start with rebuild
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Service Implementation Status

### ✅ Fully Implemented
- **Discord Adapter**: Complete FastAPI application with Discord bot integration
  - Health check endpoints (`/health`, `/health/ping`)
  - Event management routes (`/events`)
  - RSVP system (`/rsvp`)
  - Reminder functionality (`/reminders`)
  - Experience tracking (`/experience`)
  - Multi-threaded bot + API server architecture
  - Slash commands (`/register`, `/deregister`, `/tlt`)
  - Real-time Discord reaction listeners
  - Thread message moderation with emoji-only enforcement

- **MCP Gateway**: FastAPI REST server for routing MCP requests
  - Role-based routing to backend services
  - HTTP request forwarding and response handling
  - Service discovery and health checking
  - Protocol translation between REST and MCP

- **MCP Event Manager**: FastMCP 2.0 server for event and RSVP management
  - 17 MCP tools: Complete CRUD for events (create, get, update, delete, list) + emoji RSVP operations
  - 6 MCP resources for data viewing  
  - Event lifecycle management (draft → scheduled → active → completed/cancelled)
  - **Single emoji RSVP system**: Users respond with exactly one emoji (✅, ❌, 🎉, 🤔, etc.)
  - Strict validation ensures clean data for LLM evaluation pipeline
  - Event analytics with emoji breakdown and response patterns
  - User-based event filtering and creator permissions

- **MCP Photo Vibe Check**: FastMCP 2.0 server for AI photo analysis
  - LangGraph workflow for photo processing
  - OpenAI GPT-4 Vision integration
  - Rate limiting and time window validation
  - RSVP validation for photo submission
  - Slideshow generation from approved photos

- **MCP Vibe Bit**: FastMCP 2.0 server for collaborative canvas
  - PIL-based canvas rendering system
  - Emoji and color block placement
  - Real-time canvas collaboration
  - Admin canvas management
  - Rate limiting and RSVP validation

### 🚧 Placeholder Services (Empty Files)
- **Slack Adapter**: `/adapters/slack_adapter/main.py`

### 📱 Frontend Status
- **Next.js Dashboard**: Standard Next.js app template with Tailwind CSS
- Configured to run on port 3100
- Ready for custom dashboard implementation

## Environment Configuration

### Environment Variables Required
- `DISCORD_TOKEN`: Discord bot token for authentication
- `ENV`: Environment stage (development/staging/production)
- `PORT`: Service port override (defaults: 8001-8004)
- `DOMAIN`: Domain for Caddy reverse proxy configuration

### Environment Variables Optional
- `LOG_LEVEL`: Override log level for TLT service (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
  - Default: `DEBUG` for development, `INFO` for production
  - Example: `LOG_LEVEL=WARNING` to only show warnings and errors
  - Invalid values fall back to ENV-based default with warning

### Environment Files
- `.env.{ENV}`: Stage-specific environment files
- `.env`: Default fallback environment file

## Health Monitoring

### Health Check Endpoints
- Discord Adapter: `GET /health` and `GET /health/ping`
- Docker health check: `curl -f http://localhost:3100`
- Individual service health checks via supervisord

### Logging

**Centralized Log Structure:**
All services write logs to the `tlt/logs/` directory with standardized naming:

```
tlt/logs/
├── tlt_service.log         # TLT Service (FastAPI)
├── discord_adapter.log     # Discord Adapter (FastAPI + Discord Bot)
├── mcp_gateway.log         # MCP Gateway (FastAPI REST server)
├── event_manager.log       # Event Manager (FastMCP 2.0)
├── photo_vibe_check.log    # Photo Vibe Check (FastMCP 2.0)
├── vibe_bit.log           # Vibe Bit (FastMCP 2.0)
├── rsvp_service.log       # RSVP Service (FastMCP 2.0)
├── guild_manager.log      # Guild Manager (FastMCP)
└── ambient_event_agent.log # Ambient Event Agent
```

**Log Configuration:**
- **Format**: `YYYY-MM-DD HH:mm:ss,SSS - {name} - {level} - {message}`
- **Rotation**: Daily rotation with 30-day retention
- **Compression**: Automatic gzip compression of rotated logs
- **Level Control**: Environment-based (DEBUG for development, INFO for production)
- **Override**: `LOG_LEVEL` environment variable takes priority

**Other System Logs:**
- Caddy logs: `/var/log/caddy/`
- supervisord logs: `/tmp/supervisord.log`
- Docker logs: `docker-compose logs -f [service]`

## Deployment

### Fly.io Deployment
```bash
# Deploy to Fly.io
fly deploy

# Check deployment status
fly status

# View logs
fly logs
```

### Multi-Stage Docker Build Process
1. **Stage 1**: Build Next.js dashboard with Node.js
2. **Stage 2**: Install Python dependencies with Poetry
3. **Stage 3**: Create runtime container with Caddy + Python + Node.js

## Development Patterns

### Adding New Services
1. Create service directory under appropriate folder (`adapters/` or `mcp/`)
2. Implement FastAPI application with health checks
3. Add service to `supervisord.conf`
4. Update `docker-compose.yml` ports
5. Add Caddy configuration if external access needed

### Service Communication
- Use HTTP clients (requests, httpx) for inter-service communication
- Implement health checks for all services
- Use environment variables for service discovery
- Follow REST API patterns for consistency

### DateTime Handling Requirements
**CRITICAL**: All datetime objects must be properly serialized for JSON transport:

1. **Use Modern Timezone-Aware Datetimes**:
   ```python
   # ✅ CORRECT - Modern approach
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   
   # ❌ INCORRECT - Deprecated
   now = datetime.utcnow()
   ```

2. **JSON Serialization Requirements**:
   ```python
   # ✅ CORRECT - Always convert to ISO string for JSON
   created_at = datetime.now(timezone.utc).isoformat()
   
   # ❌ INCORRECT - Raw datetime objects cause "Object of type datetime is not JSON serializable"
   created_at = datetime.now(timezone.utc)
   ```

3. **CloudEvents Compatibility**:
   - All datetime fields in CloudEvents data payloads must be ISO strings
   - Use `model_dump()` instead of deprecated `dict()` for Pydantic models
   - Validate JSON serialization before sending HTTP requests

4. **Common Patterns**:
   ```python
   # Event data preparation
   event_data = {
       "created_at": datetime.now(timezone.utc).isoformat(),
       "scheduled_time": some_datetime.isoformat()
   }
   
   # CloudEvent serialization
   request_data = {
       "cloudevent": cloud_event.model_dump(),
       "priority": priority
   }
   ```

**NOTE**: This prevents JSON serialization errors like "Object of type datetime is not JSON serializable" that can break Discord adapter → TLT service communication.

### Testing Strategy
- **Organized Test Suite**: Comprehensive test scripts under `tests/` directory
- **Test Categories**: Environment, imports, health checks, and client connections
- **Test Runner**: `tests/run_all_tests.py` provides comprehensive testing workflow
- **Framework Support**: pytest for Python services, Jest for Next.js
- **Legacy Tests**: Migrated test_*.py scripts for specific features and integrations
- **Health Monitoring**: Health check endpoints serve as basic integration tests

## Common Operations

### Debugging Services
**IMPORTANT**: All debugging commands must use Poetry virtual environment.

Use the organized test suite for systematic debugging:

```bash
# Quick health check of all services
poetry run python tlt/tests/test_service_health.py

# Check environment and dependencies
poetry run python tlt/tests/test_environment.py

# Validate service imports
poetry run python tlt/tests/test_service_imports.py

# Test client connections
poetry run python tlt/tests/test_client_connections.py

# Comprehensive debugging report
poetry run python tlt/tests/run_all_tests.py
```

**Docker Debugging:**
```bash
# Check service status (Docker)
docker-compose ps

# View specific service logs (Docker)
docker-compose logs discord_adapter

# Access running container (Docker)
docker-compose exec monoapp sh

# Check supervisord status (Docker)
supervisorctl status
```

**Log Monitoring:**
```bash
# View real-time logs for specific service
tail -f tlt/logs/tlt_service.log
tail -f tlt/logs/discord_adapter.log

# View all service logs (requires multitail)
multitail tlt/logs/*.log

# Search logs for errors
grep -i error tlt/logs/*.log
grep -i "failed\|exception" tlt/logs/*.log

# View compressed rotated logs
zcat tlt/logs/tlt_service.log.gz | grep "2025-07-12"
```

**Process Management:**
```bash
# Kill service processes for restart
pkill -f "services.tlt_service.main"
pkill -f "adapters.discord_adapter.main"
```

### Configuration Updates
- **supervisord.conf**: Process management and startup commands
- **Caddyfile**: Reverse proxy routing and HTTPS configuration
- **docker-compose.yml**: Port mappings and container configuration
- **pyproject.toml**: Python dependencies and project metadata

This guide provides the foundation for understanding and developing within the TLT monorepo architecture. The system is designed for microservices scalability while maintaining development simplicity through containerization and process management.