---
version: 2
name: cross-cutting-before-implementing-updating-service-bou-4d3a
description: "FastAPI APIRouter Service Boundary Architecture: Before Implementing Updating Service Boundary Routes"
metadata:
  actual:
    adr_id: 4d3a222b-43d6-4223-a72a-9588c31b3ae9
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

# FastAPI APIRouter Service Boundary Architecture: Before Implementing Updating Service Boundary Routes

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-FBOUND-001** MUST: Before implementing or updating service boundary routes, consumers MUST resolve the exact framework and validation library versions from the project lock artifact and verify API compatibility against authoritative version documentation.

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