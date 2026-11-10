---
version: 2
name: cross-cutting-before-implementing-updating-client-comp-49dd
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Before Implementing Updating Client Components Fastmcp"
metadata:
  actual:
    adr_id: 49dd1c95-3201-4d69-8d89-e4f8123f62cc
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

# FastMCP Gateway Client for Mediated Tool and Data Access: Before Implementing Updating Client Components Fastmcp

Scope: applies to `monorepo/tlt/adapters/discord_adapter/commands/tlt/delete/**`, `monorepo/tlt/agents/ambient_event_agent/nodes/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all autonomous agent execution nodes, data retrieval, persistence, and tool operations.

### Rules

- **R-FMC-001** MUST: Before implementing or updating client components using FastMCP, the consumer MUST inspect the dependency manifest and authoritative resolution lock artifact in the repository to determine the exact locked version of FastMCP and confirm API compatibility against official documentation.
- **R-FMC-002** MUST: Implement transport instantiation within an asynchronous context manager to ensure socket and connection resources are released immediately following tool execution.
- **R-FMC-003** MUST: Configure environment-based URL discovery for the gateway client endpoint to accommodate development, staging, and production network topologies without modifying code.
- **R-FMC-004** MUST: Structure tool mapping handlers to inspect and strip internal orchestrator dispatch keys prior to forwarding parameter dictionaries to downstream tool invocations.

### Verify

```bash
# Inspect workspace configuration to identify test runner, then execute the test suite covering agent executor nodes and gateway integration
# (Repository specific test command to be executed, e.g., pytest or npm test)

# Run static analysis checks defined in repository automation configuration to detect direct service imports or gateway bypasses
# (Repository specific linter/static analysis command)

# Execute integration suites against mock gateway endpoints
```

**Accept when:**
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>