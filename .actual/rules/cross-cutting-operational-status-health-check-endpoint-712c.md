---
version: 2
name: cross-cutting-operational-status-health-check-endpoint-712c
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Operational Status Health Check Endpoints Inspect"
metadata:
  actual:
    adr_id: 712c3380-b323-4f85-b47e-e45b07bc4bab
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Operational Status Health Check Endpoints Inspect

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all modules, endpoints, and protocol handlers within the event manager service boundary that read or mutate event, RSVP, or analytics data.

### Rules

- **R-OP-001** SHOULD: Operational status and health check endpoints SHOULD inspect event manager state counters through the service module to report aggregate system health.
- **R-OP-002** MANDATORY: The consumer MUST derive tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-OP-003** MANDATORY: Before writing code that uses a versioned library, execute the lock-version grounding process in order: find dependency manifest, identify build tool, inspect lock/resolution artifact, look up official documentation for exact version, confirm every API exists, and re-run for version-sensitive behavior at point of use.
- **R-OP-004** MANDATORY: Expose domain capabilities as explicit method contracts on the service instance, avoiding direct external mutation of internal collections.
- **R-OP-005** MANDATORY: Map transport-specific input structures into domain value types before passing parameters to service operations.

### Verify

```bash
# Discover the repository test execution script from project configuration and run unit tests
# Discover workspace static analysis/linting script and execute code quality checks
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Verification is mandatory. Pull requests bypassing the domain service module or directly accessing internal collections will be blocked by code review and automated linting checks. Claude Code MUST NOT skip or defer verification.
</enforcement>