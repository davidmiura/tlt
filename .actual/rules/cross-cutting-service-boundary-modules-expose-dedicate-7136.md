---
version: 2
name: cross-cutting-service-boundary-modules-expose-dedicate-7136
description: "FastAPI APIRouter Service Boundary Architecture: Service Boundary Modules Expose Dedicated Health"
metadata:
  actual:
    adr_id: 71363074-e779-416e-b168-2efd4cd15429
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

# FastAPI APIRouter Service Boundary Architecture: Service Boundary Modules Expose Dedicated Health

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-SB-001** SHOULD: Service boundary modules SHOULD expose dedicated health check and operational monitoring routes to report readiness and subsystem connectivity.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>