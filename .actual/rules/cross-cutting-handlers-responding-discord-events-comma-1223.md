---
version: 2
name: cross-cutting-handlers-responding-discord-events-comma-1223
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Handlers Responding Discord Events Commands Use"
metadata:
  actual:
    adr_id: 12232c03-eab4-4b1c-a65e-cd5ea19f1c88
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Handlers Responding Discord Events Commands Use

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISCORD-001** MUST: Handlers responding to Discord events and commands MUST use discord.Interaction response methods to acknowledge user actions asynchronously within platform deadline limits.

### Verify

```bash
# Discover and execute the repository unit and integration test runners targeting the Discord adapter module suite
# Discover and run the repository static analysis and linting tools to confirm compliant import usage and rule adherence across all adapter components
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>