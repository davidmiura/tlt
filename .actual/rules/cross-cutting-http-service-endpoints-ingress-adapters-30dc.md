---
version: 2
name: cross-cutting-http-service-endpoints-ingress-adapters-30dc
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Http Service Endpoints Ingress Adapters Boundary"
metadata:
  actual:
    adr_id: 30dcd10f-a71e-402a-8a6d-de33f647c020
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

# FastAPI Framework Adoption for Asynchronous Service Routing: Http Service Endpoints Ingress Adapters Boundary

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HTTP-001** MUST: All HTTP service endpoints, ingress adapters, and service boundary interfaces MUST be implemented using FastAPI and modular APIRouter instances.
- **R-HTTP-002** MUST: Register modular route collections onto the root service application during lifecycle startup rather than directly declaring endpoints on the root instance.
- **R-HTTP-003** MUST: Ensure all network interactions and downstream queue dispatches within route handlers are awaited to preserve event loop concurrency.
- **R-HTTP-004** MUST: Enforce asynchronous operations for I/O and offload CPU-intensive operations to background tasks or worker pools.
- **R-HTTP-005** MUST: Maintain clean separation between transport route handlers and underlying domain service logic.

### Verify

```bash
# Discover and execute the repository test script covering API route declarations
pytest
# Discover and execute the static analysis script to verify type compatibility and route decorator compliance
flake8
```

**Accept when:**
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>