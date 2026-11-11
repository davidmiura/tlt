---
version: 2
name: cross-cutting-consumer-inspect-repository-lock-artifac-903a
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Consumer Inspect Repository Lock Artifact Determine"
metadata:
  actual:
    adr_id: 903a2028-f763-4811-950c-60d4f74a6641
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

# re Module for Precompiled Pattern Validation and Credential Redaction: Consumer Inspect Repository Lock Artifact Determine

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for inbound message content filtering, character moderation in communication adapters, batch data sanitization, image text redaction pipelines, and export data scrubbers.

### Rules

- **R-ADR-001** MUST: The consumer MUST inspect the repository lock artifact to determine the exact resolved runtime and dependency environment before executing or extending pattern matching components.
- **R-ADR-002** MUST: Define all precompiled regular expression pattern constants at module scope to guarantee single initialization upon initial load.
- **R-ADR-003** MUST: When defining character ranges for character-class validation, specify boundary code points explicitly and avoid unanchored pattern matches.

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