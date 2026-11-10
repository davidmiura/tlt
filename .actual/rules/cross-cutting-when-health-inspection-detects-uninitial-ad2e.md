---
version: 2
name: cross-cutting-when-health-inspection-detects-uninitial-ad2e
description: "FastAPI Health Check Endpoint Pattern: When Health Inspection Detects Uninitialized Dependency"
metadata:
  actual:
    adr_id: ad2ed08e-3491-4d97-a466-35c7c103221e
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

# FastAPI Health Check Endpoint Pattern: When Health Inspection Detects Uninitialized Dependency

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HC-001** MUST: When health inspection detects an uninitialized dependency, fatal exception, or non-running critical agent, the endpoint handler MUST signal degradation or failure through an appropriate HTTP error status code or status classification.

### Verify

```bash
# Discover and execute project test runner for health endpoints
pytest -k "health"
```

**Accept when:**
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

<enforcement>
Claude Code MUST NOT skip or defer verification. All registered health endpoints must be verified via automated test suites and static analysis.
</enforcement>