---
version: 2
name: cross-cutting-components-interoperating-legacy-externa-9d4e
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Interoperating Legacy External Interfaces That"
metadata:
  actual:
    adr_id: 9d4ec669-dddb-4cf8-a569-ce365b1961fd
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

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Interoperating Legacy External Interfaces That

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PATH-001** MAY: Components interoperating with legacy external interfaces that strictly demand primitive string paths MAY convert Path instances using string coercion at the immediate interface boundary.

### Verify

```bash
# Discover the project static analysis and linting command from the repository configuration and execute it to verify absence of string-based path manipulation functions.
# Discover the automated test runner command from the repository configuration and run the test suite to verify that path resolution operates correctly across all target environments.
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>