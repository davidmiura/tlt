---
version: 2
name: cross-cutting-transport-endpoints-translate-incoming-c-6732
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Transport Endpoints Translate Incoming Client Requests"
metadata:
  actual:
    adr_id: 6732cd41-f09d-4410-b189-a784761370c3
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Transport Endpoints Translate Incoming Client Requests

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all modules, endpoints, and protocol handlers within the event manager service boundary that read or mutate event, RSVP, or analytics data.

### Rules

- **R-EM-001** MUST: Transport endpoints MUST translate incoming client requests into invocations of tlt.mcp_services.event_manager.service contracts and map domain results back to external response models.

### Verify

```bash
# Discover the repository test execution script from project configuration and run unit tests covering the domain service and consuming transport handlers
# Discover workspace static analysis and linting script from project configuration and execute code quality checks across all service boundary modules
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>