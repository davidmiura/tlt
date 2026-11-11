---
version: 2
name: cross-cutting-invocation-payloads-normalize-action-arg-60f3
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Invocation Payloads Normalize Action Arguments Target"
metadata:
  actual:
    adr_id: 60f3f61f-6b34-4076-960a-0c7d2a352431
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

# FastMCP Gateway Client for Mediated Tool and Data Access: Invocation Payloads Normalize Action Arguments Target

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all agent nodes and services performing data retrieval, persistence, and tool operations across the architecture.

### Rules

- **R-GATEWAY-001** MUST: Invocation payloads MUST normalize action arguments to the target tool parameter schemas before calling call_tool and strip internal dispatch parameters that cause schema validation errors.

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