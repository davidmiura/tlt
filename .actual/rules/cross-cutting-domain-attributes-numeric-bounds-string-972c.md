---
version: 2
name: cross-cutting-domain-attributes-numeric-bounds-string-972c
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Domain Attributes Numeric Bounds String Constraints"
metadata:
  actual:
    adr_id: 972c15ea-c8f6-4e13-8e8b-65711f4ab0c5
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

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Domain Attributes Numeric Bounds String Constraints

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DOMAIN-001** MUST: Domain attributes with numeric bounds, string constraints, or required formats MUST be declared using Pydantic Field with explicit validation parameters rather than unconstrained primitive types.

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
Claude Code MUST NOT skip or defer verification. Continuous integration build failure for unvalidated boundary payloads or schema type mismatches.
</enforcement>