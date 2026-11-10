---
version: 2
name: cross-cutting-health-check-handler-function-return-0812
description: "FastAPI Health Check Endpoint Pattern: Health Check Handler Function Return Structured"
metadata:
  actual:
    adr_id: 0812e0c6-832e-4d74-a2bc-f2fabb8fb7b7
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

# FastAPI Health Check Endpoint Pattern: Health Check Handler Function Return Structured

Scope: applies to `monorepo/tlt/mcp_services/event_manager/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HLTH-001** MUST: The health check handler function MUST return a structured dictionary or response model containing at minimum an ISO 8601 UTC timestamp and an overall service status classification.

### Verify

```bash
# Discover the project test runner and execute integration and unit tests validating HTTP GET requests against registered health endpoints.
# Discover and run the project code inspection tools to verify that all service route modules register health endpoints with structured exception handling.
```

**Accept when:**
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>