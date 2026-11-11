---
version: 2
name: cross-cutting-health-check-responses-include-operation-f432
description: "FastAPI Health Check Endpoint Pattern: Health Check Responses Include Operational Telemetry"
metadata:
  actual:
    adr_id: f432de81-5e8b-4b48-afa8-12789337c35f
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

# FastAPI Health Check Endpoint Pattern: Health Check Responses Include Operational Telemetry

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all FastAPI application instances and APIRouter components deployed as network-accessible services, and routing modules that manage background workers, asynchronous task managers, or persistent queues.

### Rules

- **R-FHC-001** MAY: Health check responses MAY include operational telemetry such as queue depth, pending task count, and uptime duration when such details aid probe diagnostics without degrading handler performance.

### Verify

```bash
# Discover and execute project test runner for integration/unit tests on health endpoints
# Discover and run project code inspection tools to verify route module registration
```

**Accept when:**
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests omitting health check endpoints on new service entry points are blocked from merging.
</enforcement>