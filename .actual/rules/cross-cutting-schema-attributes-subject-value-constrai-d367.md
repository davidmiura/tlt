---
version: 2
name: cross-cutting-schema-attributes-subject-value-constrai-d367
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Schema Attributes Subject Value Constraints Numeric"
metadata:
  actual:
    adr_id: d36734be-13db-4383-98c8-e998193a8ccc
    status: accepted
    candidate_group_id: 63f40091-32f3-4392-b9da-8c66a16a77bb
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Pydantic BaseModel for Public API and Service Contract Boundaries: Schema Attributes Subject Value Constraints Numeric

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PYD-001** MUST: Schema attributes subject to value constraints, numeric ranges, or default factories MUST declare them using declarative Field descriptors within the model class rather than in procedural handler code.

### Verify

```bash
# Discover and run the project's contract validation test suite from the repository test configuration to verify that all public API schemas adhere to model validation rules.
# Execute the static type checking and schema linting routines identified in the repository build scripts to confirm type consistency across all BaseModel definitions.
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>