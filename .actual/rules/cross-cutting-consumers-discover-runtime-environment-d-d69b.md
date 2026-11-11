---
version: 2
name: cross-cutting-consumers-discover-runtime-environment-d-d69b
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Consumers Discover Runtime Environment Dependency Specifications"
metadata:
  actual:
    adr_id: d69bba6f-725f-4413-bf1d-839a806d4e45
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

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Consumers Discover Runtime Environment Dependency Specifications

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

### Rules

- **R-PATH-001** MUST: Consumers MUST discover the runtime environment dependency specifications and verify compatibility with the resolved environment baseline prior to invoking filesystem APIs.

### Verify

```bash
# Discover the project static analysis and linting command from the repository configuration and execute it to verify absence of string-based path manipulation functions.
# Discover the automated test runner command from the repository configuration and run the test suite to verify that path resolution operates correctly across all target environments.
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via static analysis checks and peer code review.
</enforcement>