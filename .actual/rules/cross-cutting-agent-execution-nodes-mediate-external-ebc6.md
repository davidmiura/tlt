---
version: 2
name: cross-cutting-agent-execution-nodes-mediate-external-ebc6
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Agent Execution Nodes Mediate External Data"
metadata:
  actual:
    adr_id: ebc6c1a7-0511-4ec8-9252-a32bb08a74fd
    status: accepted
    candidate_group_id: a6ce6494-7363-4668-88e4-78fbb3bce226
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/commands/tlt/delete/**
      - tlt/agents/ambient_event_agent/nodes/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
---

# FastMCP Gateway Client for Mediated Tool and Data Access: Agent Execution Nodes Mediate External Data

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all autonomous agent nodes and services performing data retrieval, persistence, and tool operations across the architecture.

### Rules

- **R-MCP-001** MUST: Agent execution nodes MUST mediate all external data access and service operations through FastMCP client requests routed to a centralized gateway using StreamableHttpTransport rather than making direct network calls to backend domain services.

### Verify

```bash
# Inspect the workspace configuration to identify the repository test runner, then execute the test suite covering agent executor nodes and gateway integration.
# Run static analysis checks defined in the repository automation configuration to detect any direct service imports or bypasses of the gateway transport.
# Execute integration suites against mock gateway endpoints to validate payload argument preparation and tool mapping.
```

**Accept when:**
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>