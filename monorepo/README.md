# TLT - Topic Location Time

## Table of Contents

### 📚 Documentation
- [📖 **User Guide**](USER_GUIDE.md) - Complete pictorial guide for Discord users
- [🏗️ **Architecture**](ARCHITECTURE.md) - System architecture with LangGraph agents and command flows
- [🗂️ **Guild Data Schema**](GUILD_DATA.md) - Complete data structure and storage documentation
- [🎯 **Use Cases**](USE_CASES.md) - Detailed use cases and user workflows
- [🤖 **Claude Development Guide**](CLAUDE.md) - CLAUDE.md used by claude code as directives
- [👥 **Claude Code Guide**](CLAUDE_CODE_GUIDE.md) - Developer guide for using Claude Code CLI effectively
- [🌐 **Caddy Configuration**](tlt/adapters/discord_adapter/CADDY.md) - Reverse proxy setup and configuration

### 🚀 Quick Start
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Running Services](#running-services)
- [Production Deployment](#production-deployment)

---

## Overview

TLT is a comprehensive Discord-based event management platform with AI-powered photo vibe checking, collaborative features, and intelligent automation. Built using LangGraph for agent orchestration, FastMCP for service communication, and modern Python/TypeScript technologies.

### Key Features

🎯 **Event Management**
- Discord slash commands for event creation and management
- Automated RSVP tracking with emoji-based responses
- Smart reminder system with customizable schedules
- Real-time analytics and engagement insights

🤖 **AI-Powered Features**
- Photo vibe checking with GPT-4o Vision
- LangGraph workflows for multi-stage processing
- Intelligent agent orchestration for event lifecycle
- Gen-Z style responses and community engagement

🎨 **Collaborative Tools**
- 🤝 Vibe Bit canvas for community expression
- Photo slideshow generation from event submissions
- Public and private event planning threads
- Cross-platform promotional media sharing

🔧 **Technical Architecture**
- Microservices-based with FastMCP 2.0
- Docker containerization with supervisord
- Caddy reverse proxy with HTTPS termination
- File-based state management with JSON storage

---

## Prerequisites

### System Requirements
- macOS, Linux, or Windows with WSL2
- Python 3.12.10
- Node.js 20+ (for dashboard)
- Docker and Docker Compose
- Git

### Tool Installation

```bash
# Install pipx for Python package management
brew install pipx
pipx ensurepath
sudo pipx ensurepath --global
```

*Restart Shell*

```bash
# Install Poetry for dependency management
pipx install poetry
```

*Restart Shell*

```bash
# Install Python version management
brew install virtualenv
brew install pyenv-virtualenv
pyenv install 3.12.10
```

*Restart Shell*

---

## Development Setup

### 1. Environment Setup

```bash
cd monorepo

# Set Python version
pyenv local 3.12.10

# Activate Poetry environment
eval $(poetry env activate)

# Install dependencies
poetry install --only main --no-root

# Verify setup
poetry env list
poetry env info
```

### 2. Environment Variables

Create `.env` file in the monorepo root:

```bash
# Required environment variables
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key

# Optional configuration
ENV=development
GUILD_DATA_DIR=./guild_data
LOG_LEVEL=DEBUG
```

### 3. Directory Structure

The project follows a microservices architecture:

```
monorepo/
├── tlt/
│   ├── adapters/           # Discord and Slack adapters
│   ├── mcp_services/       # MCP 2.0 services
│   ├── agents/             # LangGraph agents
│   ├── services/           # Core services
│   ├── shared/             # Shared utilities and state managers
│   └── logs/               # Centralized logging
├── nextjs_app/             # Next.js dashboard
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile              # Multi-stage build
└── supervisord.conf        # Process management
```

---

## Running Services

### Development Mode

**All services must be run with Poetry:**

```bash
# Discord Adapter (FastAPI + Discord Bot)
PYTHONPATH=. ENV=production poetry run python -m tlt.adapters.discord_adapter.main

# TLT Service (Core service with Ambient Agent)
PYTHONPATH=. ENV=production poetry run python -m tlt.services.tlt_service.main

# MCP Gateway (FastAPI/FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/gateway/main.py --transport streamable-http --port 8003

# Event Manager (FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/event_manager/main.py --transport streamable-http --port 8004

# Photo Vibe Check (FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/photo_vibe_check/main.py --transport streamable-http --port 8005

# RSVP Service (FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/rsvp/main.py --transport streamable-http --port 8007

# Vibe Bit (FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/vibe_bit/main.py --transport streamable-http --port 8006

# Guild Manager (FastMCP 2.0)
PYTHONPATH=. ENV=production poetry run fastmcp run tlt/mcp_services/guild_manager/main.py --transport streamable-http --port 8009
```

### Next.js Dashboard

```bash
cd nextjs_app/dashboard

# Install dependencies
npm install

# Run development server
npm run dev  # Runs on port 3100
```

### Caddy Reverse Proxy

```bash
cd monorepo
sudo caddy run --config tlt/adapters/discord_adapter/Caddyfile.highports --adapter caddyfile
```

### Docker Development

```bash
# Build container
docker build -t tlt/latest .

# Run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Testing

### Comprehensive Test Suite

```bash
# Run all tests
poetry run python tlt/tests/run_all_tests.py

# Individual test categories
poetry run python tlt/tests/test_environment.py         # Environment validation
poetry run python tlt/tests/test_service_imports.py     # Import validation
poetry run python tlt/tests/test_service_health.py      # Health checks
poetry run python tlt/tests/test_client_connections.py  # Connection tests

# Framework-based testing
poetry run python -m pytest tlt/tests/                  # All tests
poetry run python -m pytest tlt/tests/test_specific.py -v  # Specific test
```

### MCP Inspector

For MCP service debugging:

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector

# Access at http://localhost:6274 with provided token
```

---

## Service Ports

| Service | Port | Type | Description |
|---------|------|------|-------------|
| Next.js Dashboard | 3100 | HTTP | Web dashboard |
| Discord Adapter | 8001 | FastAPI | Discord bot and API |
| Slack Adapter | 8002 | FastAPI | Slack integration |
| MCP Gateway | 8003 | FastAPI | REST gateway |
| Event Manager | 8004 | FastMCP | Event management |
| Photo Vibe Check | 8005 | FastMCP | AI photo analysis |
| Vibe Bit | 8006 | FastMCP | Collaborative canvas |
| RSVP Service | 8007 | FastMCP | RSVP management |
| TLT Service | 8008 | FastAPI | Core service + Agent |
| Guild Manager | 8009 | FastMCP | Guild management |
| Caddy Proxy | 80/443 | HTTP/HTTPS | Reverse proxy |

---

## Production Deployment

### Environment Configuration

```bash
# Production environment variables
ENV=production
GUILD_DATA_DIR=/var/lib/tlt/guild_data
LOG_LEVEL=INFO
DOMAIN=your-domain.com

# Discord and OpenAI credentials
DISCORD_TOKEN=your_production_token
OPENAI_API_KEY=your_production_key
```

### Docker Production

```bash
# Build for production
docker build --platform linux/amd64 -t tlt/latest .

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f
```

### Fly.io Deployment

```bash
# Deploy to Fly.io
fly deploy

# Check status
fly status

# View logs
fly logs
```

---

## Key Commands

### Poetry Environment Management

```bash
# Activate Poetry environment
eval $(poetry env activate)

# Remove environment
poetry env remove 3.12

# List environments
poetry env list

# Show environment info
poetry env info
```

### Docker Cleanup

```bash
# Clean up Docker resources
docker system df
docker image prune -f
docker container prune -f
```

### Agent Development

```bash
# Generate LangGraph diagrams
poetry run python tlt/agents/ambient_event_agent/main.py --generate-diagram

# View agent help
poetry run python tlt/agents/ambient_event_agent/main.py --help
```

---

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Poetry environment is activated
2. **Port Conflicts**: Check if services are already running
3. **Missing Dependencies**: Run `poetry install --only main --no-root`
4. **Docker Issues**: Clean up containers and rebuild

### Debug Commands

```bash
# Check service health
poetry run python tlt/tests/test_service_health.py

# Validate imports
poetry run python tlt/tests/test_service_imports.py

# Check environment
poetry run python tlt/tests/test_environment.py
```

### Logging

All services write to centralized logs:

```bash
# View service logs
tail -f tlt/logs/tlt_service.log
tail -f tlt/logs/discord_adapter.log
tail -f tlt/logs/event_manager.log

# Search for errors
grep -i error tlt/logs/*.log
```

---

## Contributing

### Development Workflow

1. **Setup**: Follow the development setup instructions
2. **Testing**: Run comprehensive test suite before changes
3. **Documentation**: Update relevant documentation files
4. **Verification**: Test all affected services

### Code Standards

- **Python**: Use Poetry for dependency management
- **TypeScript**: Follow Next.js and React best practices
- **Docker**: Multi-stage builds for optimization
- **Logging**: Use structured logging with appropriate levels

### Documentation

- **Architecture**: Update ARCHITECTURE.md for system changes
- **User Guide**: Update USER_GUIDE.md for feature changes
- **Guild Data**: Update GUILD_DATA.md for schema changes
- **Use Cases**: Update USE_CASES.md for workflow changes

---

## Support

For detailed information, refer to the comprehensive documentation:

- **[User Guide](USER_GUIDE.md)** - Complete end-user documentation
- **[Architecture](ARCHITECTURE.md)** - Technical system architecture
- **[Guild Data](GUILD_DATA.md)** - Data structure and storage
- **[Use Cases](USE_CASES.md)** - Detailed workflow examples
- **[Claude Guide](CLAUDE.md)** - Development instructions
- **[Caddy Setup](tlt/adapters/discord_adapter/CADDY.md)** - Reverse proxy configuration

---

## License

This project is licensed under the terms specified in the repository. Please review the license file for details.

---

**TLT - Transforming Discord communities into sophisticated event management platforms with AI-powered features and intelligent automation.**