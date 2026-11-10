---
version: 2
name: cross-cutting-asynchronous-polling-intervals-retry-del-5488
description: "Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Asynchronous Polling Intervals Retry Delays Use"
metadata:
  actual:
    adr_id: 5488184a-ccd7-49bf-930c-f159d0542975
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

# Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Asynchronous Polling Intervals Retry Delays Use

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ASYNC-001** SHOULD: Asynchronous polling intervals and retry delays SHOULD use asyncio.sleep rather than synchronous pauses to maintain cooperative multitasking.

### Verify

```bash
# Discover and run the project test suite using the repository test runner to validate coroutine lifecycle and non-blocking task execution.
# Execute repository static analysis and asynchronous linting checks to ensure proper coroutine awaiting and absence of blocking calls.
```

**Accept when:**
- All unit and integration tests executing asynchronous routines pass without unhandled task exceptions or event loop warnings.
- Static analysis confirms asynchronous invocations use proper awaiting without unhandled futures or stalled execution.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>