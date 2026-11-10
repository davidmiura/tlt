---
version: 2
name: cross-cutting-agent-components-not-establish-direct-2cfc
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Agent Components Not Establish Direct Socket"
metadata:
  actual:
    adr_id: 2cfca7a4-bf87-4a02-b980-59494bb20e96
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

# FastMCP Gateway Client for Mediated Tool and Data Access: Agent Components Not Establish Direct Socket

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all autonomous agent execution nodes interacting with domain entity services and service integrations invoking tool-based data queries or mutation operations.

### Rules

- **R-MCP-001** MUST_NOT: Agent components MUST_NOT establish direct socket, database, or point-to-point HTTP connections to downstream domain services bypassing the centralized gateway transport.

### Verify

```bash
# Inspect workspace configuration to identify the test runner, then execute tests covering agent executor nodes and gateway integration
# Run static analysis checks to detect direct service imports or bypasses of the gateway transport
# Execute integration suites against mock gateway endpoints to validate payload argument preparation and tool mapping
```

**Accept when:**
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>