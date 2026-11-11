---
version: 2
name: cross-cutting-regular-expressions-operating-user-submi-1230
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Regular Expressions Operating User Submitted Messages"
metadata:
  actual:
    adr_id: 12303da8-0c68-4a34-ae26-02020491b136
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

# re Module for Precompiled Pattern Validation and Credential Redaction: Regular Expressions Operating User Submitted Messages

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for inbound message content filtering, character moderation in communication adapters, batch data sanitization, image text redaction pipelines, and export data scrubbers requiring detection of authentication tokens, secret keys, and platform identifiers.

### Rules

- **R-RE-001** MUST_NOT: Regular expressions operating on user-submitted messages in asynchronous event loops MUST NOT contain nested quantifiers or ambiguous alternating branches that induce polynomial or exponential backtracking.

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