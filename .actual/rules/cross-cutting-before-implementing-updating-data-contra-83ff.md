---
version: 2
name: cross-cutting-before-implementing-updating-data-contra-83ff
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Before Implementing Updating Data Contract Schemas"
metadata:
  actual:
    adr_id: 83ffbd41-19f0-49a2-a7d4-4b579738c542
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

# Pydantic BaseModel for Public API and Service Contract Boundaries: Before Implementing Updating Data Contract Schemas

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public REST endpoint request/response bodies, external webhook/CloudEvent/message broker payload ingestion schemas, and MCP tool/resource public interface parameters and response objects.

### Rules

- **R-PDS-001** MUST: Before implementing or updating data contract schemas using the data validation library, engineers MUST inspect the project lock artifact to resolve the exact dependency version and ensure schema APIs conform strictly to that resolved version.

### Verify

```bash
# Discover and run the project's contract validation test suite and static type checking routines from the repository configuration.
pytest tests/contract/
mypy .
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated schema validation suites, static type checking, and linter verification are mandatory for all public interface and cross-service boundary definitions.
</enforcement>