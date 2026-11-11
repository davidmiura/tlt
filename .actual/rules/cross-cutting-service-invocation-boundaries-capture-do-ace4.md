---
version: 2
name: cross-cutting-service-invocation-boundaries-capture-do-ace4
description: "Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Service Invocation Boundaries Capture Domain Errors"
metadata:
  actual:
    adr_id: ace46d32-a878-4a88-9e20-445f1814ca20
    status: accepted
    candidate_group_id: b71dc856-5a8f-4ad8-b897-9feef319bb16
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
---

# Adoption of tlt.mcp_services.event_manager.service Domain Service Module: Service Invocation Boundaries Capture Domain Errors

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`.

These rules are ALWAYS ACTIVE for all modules, endpoints, and protocol handlers within the event manager service boundary that read or mutate event, RSVP, or analytics data.

### Rules

- **R-SVC-001** SHOULD: Service invocation boundaries SHOULD capture domain errors and format them into appropriate protocol-specific error responses.
- **R-SVC-002** MANDATORY: Expose domain capabilities as explicit method contracts on the service instance, avoiding direct external mutation of internal collections.
- **R-SVC-003** MANDATORY: Map transport-specific input structures into domain value types before passing parameters to service operations.
- **R-SVC-004** MANDATORY (DISCOVERY POLICY): The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-SVC-005** MANDATORY (LOCK-VERSION GROUNDING): Before writing code that uses a versioned library, execute in order: 1. Find dependency manifest. 2. Identify build tool. 3. Inspect repository lock/resolution artifact. 4. Look up official docs/changelog for exact version. 5. Confirm every API/class/function exists in that version. 6. Re-run steps 3-5 per dependency at point of use.

### Verify

```bash
# Discover and run the unit test suite covering the domain service and consuming transport handlers
# Discover and execute workspace static analysis and linting scripts across service boundary modules
```

**Accept when:**
- All unit and integration tests covering domain service methods and transport adapters pass without errors.
- Static analysis confirms zero direct mutations of event or RSVP collections outside the domain service module.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites and static analysis/architectural boundary checks must be verified in continuous integration, and peer code reviews enforce these rules.
</enforcement>