---
version: 2
name: cross-cutting-before-implementing-components-depending-5689
description: "Discord Bot Adapter for Real-Time Service Integration: Before Implementing Components Depending Discord Client"
metadata:
  actual:
    adr_id: 568943e9-116f-4709-9103-634704068765
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Before Implementing Components Depending Discord Client

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for services integrating bidirectional real-time communications with Discord chat gateways and adapter components managing event threads, channel messaging, and direct message interactions.

### Rules

- **R-DISCORD-001** MUST: Before implementing components depending on Discord client libraries, engineers MUST verify the project dependency manifest and resolve the exact locked version in the repository lock artifact.
- **R-DISCORD-002** MUST: Ensure all platform gateway dispatch routines operate within non-blocking asynchronous event loops to prevent stalling gateway heartbeats.
- **R-DISCORD-003** MUST: Decouple internal transport schemas from platform-specific message embed presentations by translating payloads within bridge handlers.

### Verify

```bash
# Discover and execute the project test runner for integration tests covering adapter gateway handlers and bridge dispatchers
# Discover and run the architectural boundary linter to verify direct platform client imports remain isolated within the adapter module hierarchy
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated architectural boundary linting and pull request reviews enforce these rules.
</enforcement>