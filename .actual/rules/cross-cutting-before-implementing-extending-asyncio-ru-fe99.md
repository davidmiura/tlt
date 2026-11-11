---
version: 2
name: cross-cutting-before-implementing-extending-asyncio-ru-fe99
description: "Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Before Implementing Extending Asyncio Runtime Dependencies"
metadata:
  actual:
    adr_id: fe99ccf8-3cf6-4d54-b3de-eaf9ca8f7b80
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

# Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Before Implementing Extending Asyncio Runtime Dependencies

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ASYNC-001** MUST: Before implementing or extending asyncio runtime dependencies, consumers MUST inspect the repository lock artifact and verify the exact resolved runtime environment version.

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