---
version: 2
name: cross-cutting-route-handler-functions-that-perform-5a3a
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Route Handler Functions That Perform External"
metadata:
  actual:
    adr_id: 5a3aa371-986b-4624-bdc7-c045a3f13b1d
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

# FastAPI Framework Adoption for Asynchronous Service Routing: Route Handler Functions That Perform External

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all HTTP service endpoints, ingress adapters, and protocol service routes within the repository that perform external I/O or coordinate asynchronous background tasks.

### Rules

- **R-FASTAPI-001** MUST: Route handler functions that perform external I/O or coordinate asynchronous background tasks MUST be declared as asynchronous coroutines.

### Verify

```bash
# Discover and run the repository test execution script covering API route declarations
pytest

# Discover and run the repository static analysis script verifying type compatibility and route decorators
ruff check .
mypy .
```

**Accept when:**
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration pipelines will fail for unhandled exceptions, invalid route contracts, or non-compliant routing patterns.
</enforcement>