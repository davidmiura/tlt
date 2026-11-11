---
version: 2
name: cross-cutting-public-external-endpoints-message-ingest-28ab
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Public External Endpoints Message Ingestion Handlers"
metadata:
  actual:
    adr_id: 28abd6ec-3ddb-46d6-af96-f993212f140b
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

# Pydantic BaseModel for Public API and Service Contract Boundaries: Public External Endpoints Message Ingestion Handlers

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public external API endpoints, message ingestion handlers, and cross-service boundary methods.

### Rules

- **R-EXT-001** MUST: All public external API endpoints, message ingestion handlers, and cross-service boundary methods MUST define incoming and outgoing payload contracts as classes inheriting from Pydantic BaseModel.

### Verify

```bash
# Discover and run the project's contract validation test suite and static type checking routines
pytest tests/contract/ -v
mypy .
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification. All public boundaries must be validated using Pydantic BaseModel and verified via automated test and type-checking suites.
</enforcement>