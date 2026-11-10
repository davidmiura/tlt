---
version: 2
name: cross-cutting-outbound-http-invocations-requests-expli-6ce2
description: "Adoption of Requests Library for Outbound HTTP Client Communication: Outbound Http Invocations Requests Explicitly Declare"
metadata:
  actual:
    adr_id: 6ce229e6-f22a-43ca-8ab2-c2de1b441ccc
    status: accepted
    candidate_group_id: 4cbbfdfb-5cbc-4110-ad26-c2cece0aac40
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/photo_vibe_check/**
---

# Adoption of Requests Library for Outbound HTTP Client Communication: Outbound Http Invocations Requests Explicitly Declare

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/photo_vibe_check/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-REQ-001** MUST: All outbound HTTP invocations using requests MUST explicitly declare a timeout argument to prevent thread starvation from hanging connections.

### Verify

```bash
# Discover the repository static analysis and linting configuration to verify timeout parameter enforcement on requests calls.
# Discover the repository test runner from project configuration and execute HTTP client test suites.
```

**Accept when:**
- Static analysis and automated test suites confirm all outbound HTTP client calls specify explicit timeout parameters without unhandled blocking invocations.
- Automated test suites verify that remote network failures and timeout exceptions are gracefully handled by calling modules.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>