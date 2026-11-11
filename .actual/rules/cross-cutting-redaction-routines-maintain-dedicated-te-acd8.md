---
version: 2
name: cross-cutting-redaction-routines-maintain-dedicated-te-acd8
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Redaction Routines Maintain Dedicated Test Fixtures"
metadata:
  actual:
    adr_id: acd8f71a-bb48-4512-a2b8-1d6e1bc3f8a7
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

# re Module for Precompiled Pattern Validation and Credential Redaction: Redaction Routines Maintain Dedicated Test Fixtures

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for inbound message content filtering, character moderation in communication adapters, batch data sanitization, image text redaction pipelines, and export data scrubbers requiring detection of authentication tokens, secret keys, and platform identifiers.

### Rules

- **R-RED-001** SHOULD: Redaction routines SHOULD maintain dedicated test fixtures containing positive and negative pattern variations to verify that sensitive tokens are masked without false-positive alteration of standard payloads.

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