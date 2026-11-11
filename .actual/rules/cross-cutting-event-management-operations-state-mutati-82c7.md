---
version: 2
name: cross-cutting-event-management-operations-state-mutati-82c7
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Event Management Operations State Mutations Queries"
metadata:
  actual:
    adr_id: 82c7cf14-ad8c-4f50-9ddc-1f2a8c09c9f2
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Event Management Operations State Mutations Queries

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-EMG-001** MUST: All event management operations, state mutations, event queries, and analytics aggregations MUST be executed through the tlt.mcp_services.event_manager.service domain service module.

### Verify

```bash
# Discover the repository test execution script from the project configuration and run the unit test suite covering the domain service and its consuming transport handlers.
# Discover the workspace static analysis and linting script from the project configuration and execute code quality checks across all service boundary modules.
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>