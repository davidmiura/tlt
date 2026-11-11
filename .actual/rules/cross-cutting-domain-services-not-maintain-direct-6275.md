---
version: 2
name: cross-cutting-domain-services-not-maintain-direct-6275
description: "Discord Bot Adapter for Real-Time Service Integration: Domain Services Not Maintain Direct References"
metadata:
  actual:
    adr_id: 62750345-ec82-4021-8fe0-05815c9e3bf0
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Domain Services Not Maintain Direct References

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for services integrating bidirectional real-time communications with Discord chat gateways and adapter components managing event threads, channel messaging, and direct message interactions.

### Rules

- **R-DISCORD-001** MUST_NOT: Domain services MUST NOT maintain direct references to gateway connection sessions or raw platform message primitives outside the adapter boundary.

### Verify

```bash
# Discover and run the project test runner for integration tests covering adapter gateway handlers and bridge dispatchers
# Discover and run the architectural boundary linter to verify direct platform client imports remain isolated within the adapter module hierarchy
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>