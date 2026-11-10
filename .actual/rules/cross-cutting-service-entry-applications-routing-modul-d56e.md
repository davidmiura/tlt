---
version: 2
name: cross-cutting-service-entry-applications-routing-modul-d56e
description: "FastAPI Health Check Endpoint Pattern: Service Entry Applications Routing Modules Expose"
metadata:
  actual:
    adr_id: d56e8a17-649c-4683-89bd-4c832c034e96
    status: accepted
    candidate_group_id: ed26d008-3769-41d1-91e5-687a0247a9c4
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
      - tlt/services/tlt_service/**
---

# FastAPI Health Check Endpoint Pattern: Service Entry Applications Routing Modules Expose

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all FastAPI application instances, APIRouter components deployed as network-accessible services, and routing modules that manage background workers, asynchronous task managers, or persistent queues.

### Rules

- **R-FHC-001** MUST: All service entry applications and routing modules MUST expose an asynchronous HTTP GET endpoint at the standard health path using the FastAPI router or application decorator.

### Verify

```bash
# Discover and run the project test runner to execute integration and unit tests validating HTTP GET requests against registered health endpoints.
# Discover and run the project code inspection tools to verify that all service route modules register health endpoints with structured exception handling.
```

**Accept when:**
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

<enforcement>
Claude Code MUST NOT skip or defer verification. All new service entry points must include standardized health check endpoints, and verification checks must pass.
</enforcement>