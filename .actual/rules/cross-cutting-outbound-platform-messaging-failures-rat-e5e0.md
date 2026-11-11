---
version: 2
name: cross-cutting-outbound-platform-messaging-failures-rat-e5e0
description: "Discord Bot Adapter for Real-Time Service Integration: Outbound Platform Messaging Failures Rate Limit"
metadata:
  actual:
    adr_id: e5e07b58-9b09-4fde-a7ce-03460df5b32e
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Outbound Platform Messaging Failures Rate Limit

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all services integrating bidirectional real-time communications with chat gateways and adapter components managing event threads, channel messaging, and direct message interactions.

### Rules

- **R-DISC-001** MANDATORY: Discover all tool names, file names, commands, package managers, and version numbers from the project repository; do not assume.
- **R-LOCK-001** MANDATORY: Before writing code that uses a versioned library, find the dependency manifest, identify the build tool, inspect the repository lock or resolution artifact for exact resolved versions, look up official documentation for that exact version, confirm every API/class/function exists in that version, and re-run per dependency at point of use.
- **R-ADAPTER-001** SHOULD: Outbound platform messaging failures and rate-limit encounters SHOULD be handled with non-blocking error logging and asynchronous retries to prevent blocking gateway heartbeat loops.
- **R-ADAPTER-002** MANDATORY: Ensure all platform gateway dispatch routines operate within non-blocking asynchronous event loops to prevent stalling gateway heartbeats.
- **R-ADAPTER-003** MANDATORY: Decouple internal transport schemas from platform-specific message embed presentations by translating payloads within bridge handlers.

### Verify

```bash
# Discover the project test runner and execute the integration test suite covering adapter gateway handlers and bridge dispatchers.
# Discover and run the architectural boundary linter to verify that direct platform client imports remain isolated within the adapter module hierarchy.
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated architectural boundary linting in continuous integration pipelines and pull request reviews enforce these rules.
</enforcement>