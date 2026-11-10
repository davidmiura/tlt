---
version: 2
name: cross-cutting-text-validation-character-moderation-sen-6c73
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Text Validation Character Moderation Sensitive Token"
metadata:
  actual:
    adr_id: 6c73468b-b825-43de-8f86-99178e70c666
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

# re Module for Precompiled Pattern Validation and Credential Redaction: Text Validation Character Moderation Sensitive Token

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** MUST: All text validation, character moderation, and sensitive token redaction across adapter interfaces and batch utilities MUST use precompiled patterns created via the re module rather than runtime inline pattern parsing or ad-hoc string slicing.

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