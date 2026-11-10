---
version: 2
name: cross-cutting-long-running-asynchronous-background-ope-7114
description: "Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Long Running Asynchronous Background Operations Spawned"
metadata:
  actual:
    adr_id: 71141e4a-ade4-4d99-acbe-f154d4efe628
    status: accepted
    candidate_group_id: 78b32353-9b11-4b52-95e4-88d7e89116f5
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Long Running Asynchronous Background Operations Spawned

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ACT-001** MUST: Long-running asynchronous background operations MUST be spawned via asyncio.create_task with explicit exception tracking and cancellation handling.

### Verify

```bash
# Discover and run the project test suite using the repository test runner
# Execute repository static analysis and asynchronous linting checks
```

**Accept when:**
- All unit and integration tests executing asynchronous routines pass without unhandled task exceptions or event loop warnings.
- Static analysis confirms asynchronous invocations use proper awaiting without unhandled futures or stalled execution.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>