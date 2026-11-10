---
version: 2
name: cross-cutting-sub-service-routing-components-declare-ccc1
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Sub Service Routing Components Declare Endpoints"
metadata:
  actual:
    adr_id: ccc1af1b-be23-4ed5-b54a-63bf404bcbc8
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

# FastAPI Framework Adoption for Asynchronous Service Routing: Sub Service Routing Components Declare Endpoints

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all HTTP service endpoints, ingress adapters, and protocol service routes within the repository, including health check, metrics monitoring, and event ingestion handlers exposing HTTP transports.

### Rules

- **R-FASTAPI-001** MUST: Sub-service routing components MUST declare endpoints using APIRouter instances rather than attaching routes directly to the global application instance.

### Verify

```bash
# Discover and run repository test execution script covering API route declarations
pytest
# Discover and run repository static analysis script verifying type compatibility and route decorator compliance across all API modules
ruff check .
mypy .
```

**Accept when:**
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>