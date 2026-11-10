---
version: 2
name: cross-cutting-modal-classes-not-execute-domain-5402
description: "discord Library UI Modal Interaction and Handler Delegation: Modal Classes Not Execute Domain Entity"
metadata:
  actual:
    adr_id: 54026c77-64ac-43a2-960a-622881d6c395
    status: accepted
    candidate_group_id: 9f0c2e7b-1541-447c-b38e-c2c4c6c0d02c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# discord Library UI Modal Interaction and Handler Delegation: Modal Classes Not Execute Domain Entity

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all adapter interaction components and event bridge modules utilizing discord library UI modal primitives.

### Rules

- **R-MOD-001** MUST_NOT: Modal UI classes MUST NOT execute domain entity persistence, external network mutations, or complex business logic directly within the on_submit method body.

### Verify

```bash
# Discover and execute the repository static analysis, type checking, and test runner tools
# (Commands to be discovered from the project repository configuration)
```

**Accept when:**
- Static type analysis confirms all modal classes inherit from discord.ui.Modal and implement the required handler delegation signatures without syntax or type errors.
- Automated unit and integration test suites pass with all modal submissions delegating execution to dedicated handler methods.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by continuous integration automated static analysis, type checking suites, and peer code review.
</enforcement>