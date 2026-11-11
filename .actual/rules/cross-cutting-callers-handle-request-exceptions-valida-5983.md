---
version: 2
name: cross-cutting-callers-handle-request-exceptions-valida-5983
description: "Adoption of Requests Library for Outbound HTTP Client Communication: Callers Handle Request Exceptions Validate Status"
metadata:
  actual:
    adr_id: 5983d411-6cc6-4dd3-92b9-be2277f78861
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

# Adoption of Requests Library for Outbound HTTP Client Communication: Callers Handle Request Exceptions Validate Status

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/photo_vibe_check/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-REQ-001** SHOULD: Callers handle request exceptions and validate status codes or response payloads when executing external HTTP calls.

### Verify

```bash
# Discover the repository test runner from project configuration and execute HTTP client test suites.
# Discover the repository static analysis and linting configuration to verify timeout parameter enforcement on requests calls.
```

**Accept when:**
- Static analysis and automated test suites confirm all outbound HTTP client calls specify explicit timeout parameters without unhandled blocking invocations.
- Automated test suites verify that remote network failures and timeout exceptions are gracefully handled by calling modules.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>