---
version: 2
name: cross-cutting-components-not-execute-requests-calls-34f6
description: "Adoption of Requests Library for Outbound HTTP Client Communication: Components Not Execute Requests Calls Without"
metadata:
  actual:
    adr_id: 34f63e53-0d30-44a3-82b7-0f5602cb1380
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

# Adoption of Requests Library for Outbound HTTP Client Communication: Components Not Execute Requests Calls Without

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/photo_vibe_check/**`.

These rules are ALWAYS ACTIVE for all synchronous outbound HTTP network interactions originating from services, adapters, and agents, and all configuration validation scripts verifying remote endpoint reachability.

### Rules

- **R-REQ-001** MUST_NOT: Components MUST NOT execute requests calls without explicit timeout configurations.

### Verify

```bash
# Discover the repository test runner from project configuration and execute HTTP client test suites.
# Discover the repository static analysis and linting configuration to verify timeout parameter enforcement on requests calls.
```

**Accept when:**
- Static analysis and automated test suites confirm all outbound HTTP client calls specify explicit timeout parameters without unhandled blocking invocations.
- Automated test suites verify that remote network failures and timeout exceptions are gracefully handled by calling modules.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>