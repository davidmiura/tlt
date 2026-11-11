---
version: 2
name: cross-cutting-consumers-inspect-repository-dependency-adc8
description: "Adoption of Requests Library for Outbound HTTP Client Communication: Consumers Inspect Repository Dependency Lock Artifact"
metadata:
  actual:
    adr_id: adc8806f-8e02-433c-9334-86cd851390c4
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

# Adoption of Requests Library for Outbound HTTP Client Communication: Consumers Inspect Repository Dependency Lock Artifact

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/photo_vibe_check/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-REQ-001** MUST: Consumers MUST inspect the repository dependency lock artifact to resolve the exact locked version of the requests library before implementing client calls.

### Verify

```bash
# Discover and execute repository test suites for HTTP client interactions
# Discover and execute repository static analysis and linting configuration to verify timeout parameter enforcement
```

**Accept when:**
- Static analysis and automated test suites confirm all outbound HTTP client calls specify explicit timeout parameters without unhandled blocking invocations.
- Automated test suites verify that remote network failures and timeout exceptions are gracefully handled by calling modules.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>