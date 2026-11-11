---
version: 2
name: cross-cutting-components-requiring-filesystem-paths-pa-e7ef
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Requiring Filesystem Paths Parameters Accept"
metadata:
  actual:
    adr_id: e7ef10e4-a82e-442d-9f86-bdbeb9824789
    status: accepted
    candidate_group_id: c5305f67-e193-43d8-a4de-d0abb9bfaee8
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Requiring Filesystem Paths Parameters Accept

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

### Rules

- **R-PATH-001** SHOULD: Components requiring filesystem paths as parameters SHOULD accept Path instances directly or coerce inputs to Path objects at module boundaries.
- **R-PATH-002** MANDATORY: Anchor path discovery to the execution module location by instantiating Path from the module identity and resolving the parent directory hierarchy.
- **R-PATH-003** MANDATORY: Perform all path concatenations and child resolutions using the slash operator before evaluating path existence or reading filesystem contents.

### Verify

```bash
# Discover and execute the project static analysis and linting command
# (e.g., ruff check, flake8, or pylint as defined in repository configuration)

# Discover and execute the automated test runner command
# (e.g., pytest as defined in repository configuration)
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via static analysis checks and automated integration pipelines.
</enforcement>