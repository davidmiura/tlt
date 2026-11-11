---
version: 2
name: cross-cutting-http-route-definitions-protocol-resource-e124
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Http Route Definitions Protocol Resource Handlers"
metadata:
  actual:
    adr_id: e1247071-2edd-471b-94e7-2940be50cd74
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Http Route Definitions Protocol Resource Handlers

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all modules, endpoints, and protocol handlers within the event manager service boundary that read or mutate event, RSVP, or analytics data.

### Rules

- **R-EMC-001** MUST_NOT: HTTP route definitions and protocol resource handlers MUST NOT bypass the tlt.mcp_services.event_manager.service module to perform direct state mutations or access unexported collections.

### Verify

```bash
# Discover and run the repository test execution script covering the domain service and its consuming transport handlers
# Discover and execute the workspace static analysis and linting script across all service boundary modules
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites, static analysis, and architectural boundary checks must be executed to ensure adherence.
</enforcement>