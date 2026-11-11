---
version: 2
name: cross-cutting-coroutines-executing-primary-event-loop-8fb6
description: "Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Coroutines Executing Primary Event Loop Not"
metadata:
  actual:
    adr_id: 8fb6ca7f-e800-4c17-b308-b4177ecb13a7
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

# Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Coroutines Executing Primary Event Loop Not

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ACT-001** MUST_NOT: Coroutines executing on the primary event loop MUST NOT invoke blocking synchronous I/O operations or CPU-intensive computations that monopolize the loop thread.

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