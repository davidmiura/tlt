---
version: 2
name: cross-cutting-dynamic-path-resolution-anchored-executi-6e20
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Dynamic Path Resolution Anchored Executing Modules"
metadata:
  actual:
    adr_id: 6e20e703-bdd8-49ce-a6cc-7d49d7d63947
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

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Dynamic Path Resolution Anchored Executing Modules

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

### Rules

- **R-PATH-001** MUST: Dynamic path resolution anchored to executing modules MUST use Path object resolution rather than string-based file path inspections.

### Verify

```bash
# Discover and execute the project static analysis and linting command from the repository configuration
# Discover and execute the automated test runner command from the repository configuration
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by static analysis checks configured in the automated integration pipeline and peer code review verification during pull request reviews.
</enforcement>