---
version: 2
name: cross-cutting-gateway-responses-cached-locally-within-093d
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Gateway Responses Cached Locally Within Agent"
metadata:
  actual:
    adr_id: 093d684a-8dd2-439b-81dd-14edcad0cf43
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

# FastMCP Gateway Client for Mediated Tool and Data Access: Gateway Responses Cached Locally Within Agent

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all agent nodes and services performing data retrieval, persistence, and tool operations across the architecture.

### Rules

- **R-GW-001** MAY: Gateway responses MAY be cached locally within the agent state context for the duration of an active transaction or session when repeated reads of immutable entity metadata occur.

### Verify

```bash
# Inspect workspace configuration to identify the test runner, then execute tests covering agent executor nodes and gateway integration
# Run static analysis checks to detect any direct service imports or bypasses of the gateway transport
# Execute integration suites against mock gateway endpoints to validate payload argument preparation and tool mapping
```

**Accept when:**
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. All agent data access operations and tool executions must route exclusively through the gateway client transport.
</enforcement>