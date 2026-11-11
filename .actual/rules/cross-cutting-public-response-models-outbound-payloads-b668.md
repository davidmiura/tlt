---
version: 2
name: cross-cutting-public-response-models-outbound-payloads-b668
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Public Response Models Outbound Payloads Serialized"
metadata:
  actual:
    adr_id: b6684cb4-0d74-411f-a07f-3883cc444c2b
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

# Pydantic BaseModel for Public API and Service Contract Boundaries: Public Response Models Outbound Payloads Serialized

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PUB-001** SHOULD: Public API response models and outbound payloads SHOULD be serialized using the standard model serialization methods provided by the BaseModel class.

### Verify

```bash
# Discover and run the project's contract validation test suite from the repository test configuration
# Execute the static type checking and schema linting routines identified in the repository build scripts
pytest -v
MYPYPATH=. mypy .
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>