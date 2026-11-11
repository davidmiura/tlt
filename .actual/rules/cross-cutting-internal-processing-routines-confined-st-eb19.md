---
version: 2
name: cross-cutting-internal-processing-routines-confined-st-eb19
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Internal Processing Routines Confined Strictly Within"
metadata:
  actual:
    adr_id: eb19f346-3d8d-415a-bd2c-23f023aa4a2c
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

# Pydantic BaseModel for Public API and Service Contract Boundaries: Internal Processing Routines Confined Strictly Within

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** MAY: Internal processing routines confined strictly within a single service node MAY use typed dictionary structures for intermediate state transitions where data does not cross public or service boundaries.
- **R-MOD-002** MANDATORY: Define all input request bodies, output response representations, and cross-boundary event payloads in dedicated schema modules.
- **R-MOD-003** MANDATORY: Use Field descriptors to enforce numeric ranges, required string semantics, and default values directly in model declarations.
- **R-MOD-004** MANDATORY (LOCK-VERSION GROUNDING): Before writing code that uses a versioned library, execute in order: (1) Find the dependency manifest in the repo. (2) Identify the build tool. (3) Inspect the repository lock or resolution artifact. (4) Look up official documentation for that exact version. (5) Confirm every API/class/function exists in that version. (6) Re-run steps 3-5 per dependency at point of use.

### Verify

```bash
# Discover and run the project's contract validation test suite from the repository test configuration
# Execute the static type checking and schema linting routines identified in the repository build scripts
```

**Accept when:**
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

<enforcement>
Claude Code MUST NOT skip or defer verification. All public endpoints and cross-boundary event payloads must be validated against BaseModel rules, and static analysis/validation tests must pass without errors.
</enforcement>