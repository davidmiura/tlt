---
version: 2
name: cross-cutting-boundary-route-handlers-performing-async-dac3
description: "FastAPI APIRouter Service Boundary Architecture: Boundary Route Handlers Performing Asynchronous Background"
metadata:
  actual:
    adr_id: dac305a9-73c9-478a-9fc6-444608e0a679
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

# FastAPI APIRouter Service Boundary Architecture: Boundary Route Handlers Performing Asynchronous Background

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all HTTP endpoint controllers, route definitions, external webhook receivers, event ingestion boundaries, and operational health check declarations.

### Rules

- **R-BND-001** MUST: Boundary route handlers performing asynchronous background dispatch or external platform calls MUST be declared as asynchronous coroutine functions.

### Verify

```bash
# Discover the workspace test execution framework from repository configuration and run the route integration and contract test suites.
# Locate workspace static analysis and type checking utilities and execute them across all route boundary definitions.
```

**Accept when:**
- All boundary route handlers pass integration tests with valid and invalid payloads according to declared schema contracts.
- Static type analysis and contract validation verify zero type discrepancies between router definitions and declared response models.
- Operational and health monitoring endpoints respond with valid status payloads across all service boundary components.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated continuous integration and static analysis checks must pass without schema or type violations.
</enforcement>