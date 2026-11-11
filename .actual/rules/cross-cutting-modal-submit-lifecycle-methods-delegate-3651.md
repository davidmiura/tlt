---
version: 2
name: cross-cutting-modal-submit-lifecycle-methods-delegate-3651
description: "discord Library UI Modal Interaction and Handler Delegation: Modal Submit Lifecycle Methods Delegate Interaction"
metadata:
  actual:
    adr_id: 36517bd8-9fca-4c62-aa56-bb4557a1b36f
    status: accepted
    candidate_group_id: 9f0c2e7b-1541-447c-b38e-c2c4c6c0d02c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# discord Library UI Modal Interaction and Handler Delegation: Modal Submit Lifecycle Methods Delegate Interaction

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for adapter interaction components, event bridge modules utilizing discord library UI modal primitives, and modal dialog workflows capturing structured multi-field user input.

### Rules

- **R-MOD-001** MUST: Modal on_submit lifecycle methods MUST delegate interaction handling and extracted input values to dedicated handler instances via asynchronous handle_modal_submission calls.

### Verify

```bash
# Discover and execute repository static analysis, type checking, and test runner targeting adapter modal interaction and handler delegation test suites.
# Example discovery commands (replace with repository-specific tools):
pytest tests/adapters/
mypy src/
```

**Accept when:**
- Static type analysis confirms all modal classes inherit from discord.ui.Modal and implement the required handler delegation signatures without syntax or type errors.
- Automated unit and integration test suites pass with all modal submissions delegating execution to dedicated handler methods.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests modifying adapter interaction components must comply with modal callback delegation rules.
</enforcement>