---
version: 2
name: cross-cutting-health-check-endpoints-inspect-runtime-5f06
description: "FastAPI Health Check Endpoint Pattern: Health Check Endpoints Inspect Runtime Operational"
metadata:
  actual:
    adr_id: 5f060b10-416a-41a0-ad88-6126847eca25
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

# FastAPI Health Check Endpoint Pattern: Health Check Endpoints Inspect Runtime Operational

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HEALTH-001** SHOULD: Health check endpoints SHOULD inspect the runtime operational state of critical background managers, queues, and dependencies before resolving the health status payload.
- **R-HEALTH-002** MANDATORY: Implement health check handlers with strict internal timeouts on any external or subsystem state evaluation to prevent probe stalls.
- **R-HEALTH-003** MANDATORY: Ensure timestamps returned in health payloads use standard UTC ISO 8601 formatting.
- **R-HEALTH-004** MANDATORY: Separate lightweight liveness verification from comprehensive subsystem readiness diagnostics where deep state evaluation causes resource contention.
- **R-HEALTH-005** MANDATORY: Restrict health check responses to high-level status classifications and aggregate counters, omitting internal configuration values or credentials.

### Verify

```bash
# Discover and execute integration and unit tests validating HTTP GET requests against registered health endpoints
pytest -k "health"

# Run project code inspection tools to verify service route modules register health endpoints with structured exception handling
ruff check .
```

**Accept when:**
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

<enforcement>
Claude Code MUST NOT skip or defer verification. All new service modules must register asynchronous health route decorators, and pull requests omitting health check endpoints are blocked from merging.
</enforcement>