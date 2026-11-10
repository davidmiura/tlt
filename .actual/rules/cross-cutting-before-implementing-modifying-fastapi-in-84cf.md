---
version: 2
name: cross-cutting-before-implementing-modifying-fastapi-in-84cf
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Before Implementing Modifying Fastapi Integrations Developers"
metadata:
  actual:
    adr_id: 84cf05c2-7f9b-4f70-ab72-2092fbdadc57
    status: accepted
    candidate_group_id: 73cf1c92-ceb9-46c1-b474-e7cb2b21dc44
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/mcp_services/event_manager/**
      - tlt/services/tlt_service/**
---

# FastAPI Framework Adoption for Asynchronous Service Routing: Before Implementing Modifying Fastapi Integrations Developers

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-FASTAPI-001** MUST: Before implementing or modifying FastAPI integrations, developers MUST consult the repository dependency manifest and inspect the authoritative lock artifact to verify the exact resolved version against public documentation.
- **R-FASTAPI-002** MUST: Register modular route collections onto the root service application during lifecycle startup rather than directly declaring endpoints on the root instance.
- **R-FASTAPI-003** MUST: Ensure all network interactions and downstream queue dispatches within route handlers are awaited to preserve event loop concurrency.
- **R-FASTAPI-004** MUST: Execute lock-version grounding steps in order (find manifest, identify build tool, inspect lock artifact, look up official version-specific documentation, confirm API existence, re-run at point of use for version-sensitive behavior) before writing code that uses a versioned library.
- **R-FASTAPI-005** MUST: Offload CPU-intensive operations to background tasks or worker pools and enforce asynchronous operations for I/O to prevent event loop starvation.
- **R-FASTAPI-006** MUST: Maintain clean separation between transport route handlers and underlying domain service logic.

### Verify

```bash
# Discover the repository test execution script and run the automated integration test suite covering API route declarations.
# Discover the repository static analysis script and verify type compatibility and route decorator compliance across all API modules.
```

**Accept when:**
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>