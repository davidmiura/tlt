---
version: 2
name: cross-cutting-http-endpoints-accepting-external-trigge-913c
description: "Discord Bot Adapter for Real-Time Service Integration: Http Endpoints Accepting External Triggers Chat"
metadata:
  actual:
    adr_id: 913cf069-1015-4a07-bff7-c01e022f397d
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Http Endpoints Accepting External Triggers Chat

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISC-001** MUST: HTTP endpoints accepting external triggers for chat platform dispatch MUST validate incoming payloads using strict data schema models before scheduling asynchronous delivery.

### Verify

```bash
# Discover and execute the project test runner for integration tests covering adapter gateway handlers and bridge dispatchers
# Discover and run the architectural boundary linter to verify direct platform client imports remain isolated within the adapter module hierarchy
```

**Accept when:**
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated architectural boundary linting in CI pipelines and PR reviews by integration engineering teams.
</enforcement>