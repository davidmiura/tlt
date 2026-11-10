---
version: 2
name: cross-cutting-route-handlers-not-return-unstructured-9155
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Route Handlers Not Return Unstructured Error"
metadata:
  actual:
    adr_id: 9155b2a9-e15f-457f-81dc-e0035a1d31b7
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

# FastAPI Framework Adoption for Asynchronous Service Routing: Route Handlers Not Return Unstructured Error

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all HTTP service endpoints, ingress adapters, and protocol service routes within the repository, including all health check, metrics monitoring, and event ingestion handlers exposing HTTP transports.

### Rules

- **R-ROUTE-001** MUST_NOT: Route handlers MUST NOT return unstructured error payloads or unhandled raw exceptions; failures MUST be signaled via standard HTTPException instances.
- **R-ROUTE-002** MANDATORY: The consumer MUST discover tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-ROUTE-003** MANDATORY: Before writing code that uses a versioned library, execute in order: (1) Find the dependency manifest in the repo. (2) Identify the build tool. (3) Inspect the repository lock or resolution artifact to determine exact resolved version. (4) Look up official documentation for that exact version. (5) Confirm every API, class, or function exists in that version. (6) Re-run steps 3-5 per dependency at point of use.
- **R-ROUTE-004** MANDATORY: Register modular route collections onto the root service application during lifecycle startup rather than directly declaring endpoints on the root instance.
- **R-ROUTE-005** MANDATORY: Ensure all network interactions and downstream queue dispatches within route handlers are awaited to preserve event loop concurrency.

### Verify

```bash
# Discover and run the repository test execution script covering API route declarations
# Discover and run the repository static analysis script verifying type compatibility and route decorator compliance across all API modules
pytest
ruff check .
```

**Accept when:**
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. All public HTTP endpoints must use modular routers, avoid unstructured errors, and pass static analysis and integration test suites.
</enforcement>