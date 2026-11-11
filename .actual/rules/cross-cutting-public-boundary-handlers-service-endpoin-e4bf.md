---
version: 2
name: cross-cutting-public-boundary-handlers-service-endpoin-e4bf
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Public Boundary Handlers Service Endpoints Not"
metadata:
  actual:
    adr_id: e4bfbda8-8dfa-41c1-b4e6-add936a110cc
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

# Pydantic BaseModel for Public API and Service Contract Boundaries: Public Boundary Handlers Service Endpoints Not

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PUB-001** MUST_NOT: Public boundary handlers and service endpoints MUST NOT accept unvalidated dictionaries or untyped mapping structures as contract parameters when structured payload schemas are defined.

### Verify

```bash
# Discover and run the project's contract validation test suite from the repository test configuration to verify that all public API schemas adhere to model validation rules.
pytest tests/contract/
# Execute the static type checking and schema linting routines identified in the repository build scripts to confirm type consistency across all BaseModel definitions.
mypy .
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification. All public boundaries must utilize BaseModel schemas.
</enforcement>