---
version: 2
name: cross-cutting-engineers-discover-ecosystem-lock-artifa-5e6d
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Engineers Discover Ecosystem Lock Artifact Repository"
metadata:
  actual:
    adr_id: 5e6d92a9-3e77-4229-a4b0-10e492e2d90b
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

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Engineers Discover Ecosystem Lock Artifact Repository

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PYD-001** MUST: Engineers MUST discover the ecosystem lock artifact in the repository and verify the exact resolved version of Pydantic before introducing or modifying model schemas, consulting the version-matched documentation.

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
Claude Code MUST NOT skip or defer verification. Verification of domain model validation, static type checks, and schema compatibility is mandatory.
</enforcement>