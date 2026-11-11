---
version: 2
name: cross-cutting-complex-cross-field-validations-semantic-6301
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Complex Cross Field Validations Semantic Invariants"
metadata:
  actual:
    adr_id: 63018335-de24-43ae-9319-fb99ff5c5f77
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

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Complex Cross Field Validations Semantic Invariants

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-VAL-001** SHOULD: Complex cross-field validations and semantic invariants SHOULD be implemented using Pydantic validator decorators on the enclosing model.

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
Claude Code MUST NOT skip or defer verification. Continuous integration will fail for unvalidated boundary payloads or schema type mismatches, and pull requests introducing unstructured dictionaries at public service interfaces will be rejected.
</enforcement>