---
version: 2
name: cross-cutting-consumer-inspect-authoritative-dependenc-e58c
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Consumer Inspect Authoritative Dependency Resolution Lock"
metadata:
  actual:
    adr_id: e58c349f-06af-415c-8a28-bafe6467d3b5
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Consumer Inspect Authoritative Dependency Resolution Lock

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all modules, endpoints, and protocol handlers within the event manager service boundary that read or mutate event, RSVP, or analytics data.

### Rules

- **R-ADR-001** MUST: The consumer MUST inspect the authoritative dependency resolution lock artifact to verify exact dependency versions before implementing or updating service integrations.

### Verify

```bash
# Discover the repository test execution script from project configuration and run unit tests
# Discover the workspace static analysis and linting script and execute code quality checks
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>