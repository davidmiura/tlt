---
version: 2
name: cross-cutting-event-bridge-handlers-coordinating-modal-fd14
description: "discord Library UI Modal Interaction and Handler Delegation: Event Bridge Handlers Coordinating Modal Submissions"
metadata:
  actual:
    adr_id: fd1454ba-53f5-49e4-bfb7-e8c1f3dfa56a
    status: accepted
    candidate_group_id: 9f0c2e7b-1541-447c-b38e-c2c4c6c0d02c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# discord Library UI Modal Interaction and Handler Delegation: Event Bridge Handlers Coordinating Modal Submissions

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MODAL-001** SHOULD: Event bridge handlers coordinating modal submissions SHOULD route execution through matching dedicated handler instances to maintain consistent payload processing across adapter entry points.

### Verify

```bash
# Discover and execute the repository static analysis, type checking, and test runner tools targeting adapter modal interaction and handler delegation
```

**Accept when:**
- Static type analysis confirms all modal classes inherit from discord.ui.Modal and implement the required handler delegation signatures without syntax or type errors.
- Automated unit and integration test suites pass with all modal submissions delegating execution to dedicated handler methods.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests modifying adapter interaction components must comply with these delegation and testing rules.
</enforcement>