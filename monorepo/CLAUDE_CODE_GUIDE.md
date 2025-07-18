# Claude Code Development Guide

This guide provides developers with comprehensive instructions for using Claude Code effectively with the TLT monorepo project.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation & Setup](#installation--setup)
- [Project Integration](#project-integration)
- [Development Workflow](#development-workflow)
- [Best Practices](#best-practices)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## Quick Start

Claude Code is Anthropic's official CLI tool that provides an interactive AI assistant for software development tasks. It's particularly powerful for complex codebases like TLT's microservices architecture.

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Start interactive session
claude-code

# Check version
claude-code --version
```

## Installation & Setup

### Prerequisites

1. **Node.js**: Use LTS version (Iron recommended)
   ```bash
   nvm use lts/iron
   ```

2. **Claude Code CLI**: Install globally
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

3. **Authentication**: Set up your Anthropic API key
   ```bash
   # Add to your shell profile (.bashrc, .zshrc, etc.)
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

### Verification

```bash
claude-code --version
claude --version  # Shorthand command
claude            # Start interactive session
```

## Project Integration

### TLT Monorepo Context

Claude Code excels with the TLT project because it can:

- **Navigate Complex Architecture**: Understand microservices relationships between Discord adapters, MCP services, and Next.js dashboard
- **Multi-Language Support**: Work with Python (FastAPI, FastMCP), TypeScript (Next.js), and Docker configurations
- **Service Orchestration**: Help with Docker Compose, supervisord, and Caddy proxy configurations
- **Testing Workflows**: Execute comprehensive test suites and debug service health

### Key Project Files for Claude Code

When working with Claude Code, these files provide essential context:

```bash
# Core documentation (always provide context)
CLAUDE.md                    # Main development guide
ARCHITECTURE.md             # System architecture
GUILD_DATA.md               # Data schema and storage
USER_GUIDE.md               # End-user workflows

# Configuration files
docker-compose.yml          # Service orchestration
supervisord.conf           # Process management
pyproject.toml             # Python dependencies
Dockerfile                 # Container build config

# Service entry points
tlt/adapters/discord_adapter/main.py    # Discord bot + API
tlt/services/tlt_service/main.py        # Core TLT service
tlt/mcp_services/*/main.py              # MCP services
nextjs_app/dashboard/                   # Next.js frontend
```

## Development Workflow

### 1. Starting a Development Session

```bash
# Navigate to project root
cd /path/to/tlt/monorepo

# Start Claude Code session
claude-code

# Provide project context immediately
# Upload CLAUDE.md or paste key sections
```

### 2. Common Development Tasks

**Service Development:**
```
"Help me debug the Discord adapter health endpoint"
"Add a new MCP tool to the event manager service"
"Optimize the photo vibe check LangGraph workflow"
```

**Architecture Changes:**
```
"Add a new microservice for user analytics"
"Update the Docker Compose configuration for scaling"
"Modify the Caddy reverse proxy for new endpoints"
```

**Testing & Debugging:**
```
"Run the comprehensive test suite and fix any failures"
"Debug why the event manager MCP service won't start"
"Optimize Poetry dependency management"
```

### 3. Multi-Service Operations

Claude Code can handle complex operations across services:

```bash
# Example: Adding a new feature across multiple services
"Implement user preference storage:
1. Add database schema to event manager
2. Create API endpoints in Discord adapter  
3. Update Next.js dashboard UI
4. Add MCP tools for preference management"
```

## Best Practices

### 1. Provide Rich Context

**Always include:**
- Current branch and git status
- Service architecture overview
- Relevant environment variables
- Recent error logs or issues

**Example context:**
```
I'm working on the TLT Discord event management platform. 
Current branch: feature/user-preferences
Services running: Discord adapter (8001), Event manager (8004)
Issue: MCP gateway returning 500 errors when routing to event manager
Logs: [paste relevant log entries]
```

### 2. Use Incremental Development

```bash
# Break complex tasks into steps
"Let's add user preferences in phases:
1. First, design the data schema
2. Then implement MCP tools
3. Finally, add Discord slash commands"
```

### 3. Leverage Claude Code's Strengths

**Code Analysis:**
- "Analyze the event lifecycle in the event manager service"
- "Review the LangGraph workflow for potential optimizations"
- "Identify security vulnerabilities in the API endpoints"

**Refactoring:**
- "Refactor the Discord bot command handling for better modularity"
- "Extract common utilities from MCP services into shared modules"
- "Optimize Docker layer caching in the multi-stage build"

**Documentation:**
- "Generate API documentation for the MCP gateway service"
- "Update the architecture diagram to reflect new services"
- "Create developer onboarding checklist"

### 4. Poetry Integration

Always specify Poetry usage for Python development:

```bash
# Correct approach
"Run the event manager service using Poetry:
poetry run python -m tlt.mcp_services.event_manager.main"

# Include dependency management
"Add a new Python dependency for JSON schema validation and update pyproject.toml"
```

## Common Commands

### Project Navigation

```bash
# Start with project overview
"Show me the current service architecture and health status"

# Explore specific services
"Analyze the Discord adapter service structure and dependencies"
"Review the MCP gateway routing logic"
```

### Development Operations

```bash
# Service management
"Start all development services with proper Poetry environment"
"Debug why the photo vibe check service isn't responding"
"Update the Next.js dashboard to use the latest API endpoints"

# Testing workflows
"Run the comprehensive test suite and summarize results"
"Create integration tests for the new user preference feature"
"Validate all MCP services are properly configured"
```

### Code Quality

```bash
# Code review
"Review the recent changes in the event manager for best practices"
"Suggest optimizations for the LangGraph photo processing workflow"
"Check for security issues in the Discord bot token handling"

# Documentation
"Update the API documentation to reflect the new endpoints"
"Generate usage examples for the MCP tools"
"Create troubleshooting guide for common deployment issues"
```

## Troubleshooting

### Common Issues

1. **Poetry Environment Problems**
   ```bash
   "Help me fix Poetry virtual environment activation issues"
   "Debug why Poetry can't find the Python modules"
   ```

2. **Service Communication Failures**
   ```bash
   "The Discord adapter can't reach the MCP gateway - debug the connection"
   "MCP services are returning timeout errors - check the FastMCP configuration"
   ```

3. **Docker Build Issues**
   ```bash
   "The multi-stage Docker build is failing on the Python dependency install"
   "Optimize the Dockerfile for faster builds and smaller image size"
   ```

### Debug Commands

```bash
# Health checks
"Run the test suite to identify which services are failing"

# Log analysis  
"Analyze the recent error logs to identify the root cause"

# Configuration validation
"Verify all environment variables and configuration files are correct"
```

## Advanced Features

### 1. Multi-File Operations

Claude Code excels at cross-file operations:

```bash
"Rename the function `get_event_data` to `fetch_event_details` across all services"
"Update all MCP service configurations to use the new logging format"
"Migrate from FastAPI to FastMCP 2.0 for the remaining adapter services"
```

### 2. Architecture Evolution

```bash
"Plan the migration from file-based storage to PostgreSQL:
1. Design database schema
2. Create migration scripts  
3. Update all services to use database
4. Add connection pooling and error handling"
```

### 3. Performance Optimization

```bash
"Profile the photo vibe check service and optimize bottlenecks"
"Analyze Docker container resource usage and suggest improvements"
"Review the LangGraph workflows for efficiency improvements"
```

## Integration with TLT Workflows

### Git Integration

```bash
# Branch management
"Create a feature branch for user analytics and set up the development environment"

# Commit workflows
"Review my changes and create appropriate git commits with descriptive messages"
```

### Deployment Assistance

```bash
# Docker operations
"Build and test the production Docker image"
"Update docker-compose.yml for the new service configuration"

# Fly.io deployment
"Prepare the project for Fly.io deployment and update fly.toml"
```

### Testing Integration

```bash
# Comprehensive testing
"Execute the full test suite including environment, imports, health, and connections"
"Create end-to-end tests for the Discord event creation workflow"
```

## Resources

### Official Documentation
- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic API Documentation](https://docs.anthropic.com/)

### TLT Project Documentation
- [Main Development Guide](CLAUDE.md) - Comprehensive development instructions
- [System Architecture](ARCHITECTURE.md) - LangGraph agents and service flows
- [User Guide](USER_GUIDE.md) - Complete Discord user workflows
- [Guild Data Schema](GUILD_DATA.md) - Data structure documentation

### Community Resources
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
- [Anthropic Discord Community](https://discord.gg/anthropic)
- [FastMCP Documentation](https://modelcontextprotocol.io/quickstart)

---

## Quick Reference

### Essential Commands
```bash
# Installation
npm install -g @anthropic-ai/claude-code

# Start session
claude-code

# With project context
claude-code --resume  # Resume previous session
```

### Key TLT Commands for Claude Code
```bash
# Always use Poetry for Python
poetry run python -m tlt.adapters.discord_adapter.main

# Test everything
poetry run python tlt/tests/run_all_tests.py

# Build and deploy
docker-compose up --build
```

### Best Practices Summary
1. **Always provide project context** from CLAUDE.md
2. **Use Poetry** for all Python operations  
3. **Break complex tasks** into incremental steps
4. **Include error logs** and environment details
5. **Leverage multi-service** architecture understanding

---

**Claude Code + TLT = Powerful development acceleration for complex microservices architectures.**