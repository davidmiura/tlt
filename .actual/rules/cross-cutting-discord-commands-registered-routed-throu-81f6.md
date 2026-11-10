---
version: 2
name: cross-cutting-discord-commands-registered-routed-throu-81f6
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Discord Commands Registered Routed Through App"
metadata:
  actual:
    adr_id: 81f68e08-eab8-40b9-a5c9-ae1f27f7cc1a
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Discord Commands Registered Routed Through App

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all modules and classes within the Discord adapter boundary interacting with the Discord Gateway, application commands, or user interface components, and scheduled background routines managing periodic checks or automated reminder broadcasts within the Discord client runtime.

### Rules

- **R-DISC-001** MUST: All Discord commands MUST be registered and routed through discord.app_commands application command trees and handled by discrete handler classes rather than legacy text message prefixes.
- **R-DISC-002** MANDATORY: Execute the Lock-Version Grounding procedure (find dependency manifest, identify build tool, inspect lock/resolution artifact for exact version, look up official documentation for that exact version, confirm every API/class/function exists in that version) before writing code that uses a versioned library.
- **R-DISC-003** MANDATORY: Maintain strict isolation between Discord UI elements such as views, selects, and modals and core domain service clients by delegating via bridge handlers.
- **R-DISC-004** MANDATORY: Ensure all interaction responses acknowledge user actions within platform latency limits to prevent expired interaction tokens.
- **R-DISC-005** MANDATORY: Structure slash commands within centralized command routers and register handlers asynchronously during client startup hooks.

### Verify

```bash
# Discover and execute repository unit and integration test runners targeting the Discord adapter module suite
# Discover and run repository static analysis and linting tools to confirm compliant import usage and rule adherence
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites, static analysis linters, and peer code reviews enforce compliance, and pull requests violating these boundaries will be blocked.
</enforcement>