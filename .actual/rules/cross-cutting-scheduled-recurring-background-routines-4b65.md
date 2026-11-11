---
version: 2
name: cross-cutting-scheduled-recurring-background-routines-4b65
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Scheduled Recurring Background Routines Within Discord"
metadata:
  actual:
    adr_id: 4b65f7ed-48f6-4f7a-aadc-55fde3f567ad
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Scheduled Recurring Background Routines Within Discord

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISCORD-001** MUST: Scheduled and recurring background routines within the Discord client runtime MUST utilize discord.ext.tasks loop decorators rather than unmanaged background threads.

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