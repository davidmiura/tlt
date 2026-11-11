---
version: 2
name: cross-cutting-subpath-navigation-utilize-slash-operato-a361
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Subpath Navigation Utilize Slash Operator Path"
metadata:
  actual:
    adr_id: a361b2a8-6c6a-4d08-bd3f-a5aed88b6992
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

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Subpath Navigation Utilize Slash Operator Path

Scope: applies to `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

### Rules

- **R-PATH-001** SHOULD: Subpath navigation SHOULD utilize the slash operator on Path objects to assemble filesystem paths declaratively.

### Verify

```bash
# Discover and run the project static analysis and linting command
# Discover and run the automated test suite command
```

**Accept when:**
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by static analysis checks in the automated integration pipeline and peer code review verification during pull request reviews.
</enforcement>