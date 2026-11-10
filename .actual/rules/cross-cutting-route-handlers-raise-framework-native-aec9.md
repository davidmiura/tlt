---
version: 2
name: cross-cutting-route-handlers-raise-framework-native-aec9
description: "FastAPI APIRouter Service Boundary Architecture: Route Handlers Raise Framework Native Http"
metadata:
  actual:
    adr_id: aec93ba0-e7eb-46d8-bc15-b5e2ef4cb807
    status: accepted
    candidate_group_id: a0b3689c-1ef1-4735-b714-080fde0d23b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# FastAPI APIRouter Service Boundary Architecture: Route Handlers Raise Framework Native Http

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all HTTP endpoint controllers, route definitions across service adapters, core services, external webhook receivers, event ingestion boundaries, and operational health check declarations.

### Rules

- **R-ROUTE-001** MUST: Route handlers MUST raise framework-native HTTP exception instances with explicit HTTP status codes and detail payloads when encountering domain errors or unresolvable resources, rather than returning raw error strings or untyped dictionary failures.

### Verify

```bash
# Discover the workspace test execution framework from repository configuration and run the route integration and contract test suites.
# Locate the workspace static analysis and type checking utilities from the project configuration and execute them across all route boundary definitions.
```

**Accept when:**
- All boundary route handlers pass integration tests with valid and invalid payloads according to declared schema contracts.
- Static type analysis and contract validation verify zero type discrepancies between router definitions and declared response models.
- Operational and health monitoring endpoints respond with valid status payloads across all service boundary components.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated continuous integration test suites, static type analysis, and schema validation checks executed during pipeline verification.
</enforcement>