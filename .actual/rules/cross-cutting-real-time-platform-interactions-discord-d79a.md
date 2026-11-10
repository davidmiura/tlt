---
version: 2
name: cross-cutting-real-time-platform-interactions-discord-d79a
description: "Discord Bot Adapter for Real-Time Service Integration: Real Time Platform Interactions Discord Isolated"
metadata:
  actual:
    adr_id: d79a3701-25e4-4cf6-ae98-08e23d2d6ff4
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Real Time Platform Interactions Discord Isolated

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISCORD-001** MUST: All real-time platform interactions with Discord MUST be isolated within dedicated adapter components subclassing the platform bot command client, separating gateway lifecycle management from internal service domain logic.

### Verify

```bash
# Discover and run the architectural boundary linter to verify that direct platform client imports remain isolated within the adapter module hierarchy.
# Discover the project test runner and execute the integration test suite covering adapter gateway handlers and bridge dispatchers.
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated architectural boundary linting and pull request reviews enforce these rules.
</enforcement>