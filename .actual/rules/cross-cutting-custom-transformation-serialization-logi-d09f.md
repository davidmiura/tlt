---
version: 2
name: cross-cutting-custom-transformation-serialization-logi-d09f
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Custom Transformation Serialization Logic Complex Types"
metadata:
  actual:
    adr_id: d09fff70-1cb3-41e5-bc8c-af4d9fdbc66a
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

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Custom Transformation Serialization Logic Complex Types

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PYD-001** SHOULD: Custom transformation and serialization logic for complex types SHOULD utilize Pydantic field serializer methods to maintain uniform schema representation across transport layers.

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
Claude Code MUST NOT skip or defer verification. Continuous integration builds fail for unvalidated boundary payloads or schema type mismatches.
</enforcement>