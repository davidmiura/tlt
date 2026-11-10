---
version: 2
name: cross-cutting-discord-adapter-subsystem-use-along-42bb
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Discord Adapter Subsystem Use Along Ext"
metadata:
  actual:
    adr_id: 42bb5fa0-e365-4d1c-ac9b-2fc3f0d514c4
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Discord Adapter Subsystem Use Along Ext

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all modules and classes within the Discord adapter boundary interacting with the Discord Gateway, application commands, or user interface components, and scheduled background routines managing periodic checks or automated reminder broadcasts within the Discord client runtime.

### Rules

- **R-DISCORD-001** MUST: The Discord adapter subsystem MUST use discord.py along with discord.ext and discord.ui as the exclusive framework for Discord Gateway connectivity, application command trees, and interactive UI components.
- **R-DISCORD-002** MUST: Maintain strict isolation between Discord UI elements such as views, selects, and modals and core domain service clients by delegating via bridge handlers.
- **R-DISCORD-003** MUST: Ensure all interaction responses acknowledge user actions within platform latency limits to prevent expired interaction tokens.
- **R-DISCORD-004** MUST: Structure slash commands within centralized command routers and register handlers asynchronously during client startup hooks.

### Verify

```bash
# Discover and execute repository unit and integration test runners targeting the Discord adapter module suite
# Discover and run repository static analysis and linting tools to confirm compliant import usage and rule adherence across all adapter components
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>