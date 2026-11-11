---
version: 2
name: cross-cutting-asynchronous-messaging-operations-channe-65ef
description: "Discord Bot Adapter for Real-Time Service Integration: Asynchronous Messaging Operations Channels Threads Direct"
metadata:
  actual:
    adr_id: 65ef01b3-0391-422c-9a9a-cb2e08956981
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Asynchronous Messaging Operations Channels Threads Direct

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for services integrating bidirectional real-time communications with chat platform gateways and adapter components managing event threads, channel messaging, and direct message interactions.

### Rules

- **R-DISC-001** MUST: Asynchronous messaging operations to channels, threads, and direct messages MUST be dispatched through designated bridge handlers rather than direct invocations from business controllers.

### Verify

```bash
# Discover the project test runner and execute the integration test suite covering adapter gateway handlers and bridge dispatchers.
# Discover and run the architectural boundary linter to verify that direct platform client imports remain isolated within the adapter module hierarchy.
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated architectural boundary linting, pull request reviews, and continuous integration pipelines.
</enforcement>