---
version: 2
name: cross-cutting-each-tool-invocation-dispatched-fastmcp-ae20
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Each Tool Invocation Dispatched Fastmcp Utilize"
metadata:
  actual:
    adr_id: ae20d492-5082-407e-83dc-9ecfda99a996
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

# FastMCP Gateway Client for Mediated Tool and Data Access: Each Tool Invocation Dispatched Fastmcp Utilize

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all agent nodes and services performing data retrieval, persistence, and tool operations across the architecture.

### Rules

- **R-FMC-001** MUST: Each tool invocation dispatched to FastMCP MUST utilize asynchronous context management via Client with StreamableHttpTransport and provide client identity metadata.

### Verify

```bash
# Inspect workspace configuration to identify the test runner, then execute tests covering agent executor nodes and gateway integration
# Run static analysis checks defined in the repository automation configuration to detect direct service imports or gateway bypasses
# Execute integration suites against mock gateway endpoints to validate payload argument preparation and tool mapping
```

**Accept when:**
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by continuous integration test suites, static code analysis, and peer code reviews.
</enforcement>