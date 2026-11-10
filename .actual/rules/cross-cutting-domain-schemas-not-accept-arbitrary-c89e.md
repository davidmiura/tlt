---
version: 2
name: cross-cutting-domain-schemas-not-accept-arbitrary-c89e
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Domain Schemas Not Accept Arbitrary Untyped"
metadata:
  actual:
    adr_id: c89e7f32-63ef-4dec-963f-bc2bf42242e0
    status: accepted
    candidate_group_id: 89a6d983-d0c6-439d-b9f8-f482f84c00df
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Domain Schemas Not Accept Arbitrary Untyped

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DOMAIN-001** MUST_NOT: Domain schemas MUST_NOT accept arbitrary untyped dictionary payloads at boundary interfaces without parsing and validating them through their designated BaseModel schema.

### Verify

```bash
# Discover and run the project test execution command that targets domain model validation test suites.
# Discover and execute the project static type analysis command to verify that all domain model fields have valid type annotations.
# Discover and execute the project schema verification command to confirm contract compatibility across service boundaries.
```

**Accept when:**
- All domain models subclass BaseModel and enforce business invariants via Field constraints or validator methods.
- Automated test suites verifying boundary rejection of invalid payloads pass without failures.
- Static type analysis executes across all model definitions with zero type errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated test suites, static type checking during CI, and peer code reviews.
</enforcement>