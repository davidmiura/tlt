---
version: 2
name: cross-cutting-pattern-instances-compiled-once-module-1394
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Pattern Instances Compiled Once Module Initialization"
metadata:
  actual:
    adr_id: 1394ed77-aa2b-475e-91a5-ee822262fc9c
    status: accepted
    candidate_group_id: 7812eaa4-5196-4b53-91a2-64db19f1be66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/scripts/**
---

# re Module for Precompiled Pattern Validation and Credential Redaction: Pattern Instances Compiled Once Module Initialization

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** MUST: Pattern instances MUST be compiled once at module initialization using re.compile rather than repeatedly recompiled within message event loops or batch iteration blocks.

### Verify

```bash
test -n "$REPOSITORY_TEST_SUITE" && $REPOSITORY_TEST_SUITE || echo "Execute test suite discovered from repository manifest"
test -n "$REPOSITORY_LINTER" && $REPOSITORY_LINTER || echo "Execute linting suite discovered from repository manifest"
```

**Accept when:**
- All unit and integration tests validating pattern matching and redaction utilities pass successfully without errors.
- Zero unanchored dynamic regular expression compilations exist within message handling loops or batch iteration paths.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>