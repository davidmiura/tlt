---
version: 2
name: cross-cutting-regular-expressions-designed-token-sanit-2c9f
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Regular Expressions Designed Token Sanitization Credential"
metadata:
  actual:
    adr_id: 2c9f7fbd-8924-4b80-9c2f-e7a6f169c04f
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

# re Module for Precompiled Pattern Validation and Credential Redaction: Regular Expressions Designed Token Sanitization Credential

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for inbound message content filtering, character moderation in communication adapters, batch data sanitization, image text redaction pipelines, and export data scrubbers.

### Rules

- **R-CRE-001** MUST: Regular expressions designed for token sanitization and credential masking MUST match full structural delimiters and boundary anchors to prevent partial redaction or collateral corruption of non-sensitive metadata.

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