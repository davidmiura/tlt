---
version: 2
name: cross-cutting-engineers-not-use-nested-string-e660
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Engineers Not Use Nested String Based"
metadata:
  actual:
    adr_id: e6602bc2-dfb9-4c63-9173-8c6f19e5ca29
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

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Engineers Not Use Nested String Based

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

### Rules

- **R-PATH-001** MUST_NOT: Engineers MUST NOT use nested string-based directory traversal functions or raw string concatenations for constructing filesystem paths.

### Verify

```bash
# Discover and run static analysis/linting command to verify absence of string-based path manipulation functions
# Discover and run automated test runner command to verify that path resolution operates correctly across all target environments
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via static analysis checks and peer code review.
</enforcement>