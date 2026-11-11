---
version: 2
name: cross-cutting-interactive-discord-components-implement-accc
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Interactive Discord Components Implemented Extending View"
metadata:
  actual:
    adr_id: acccd8a3-453c-4d94-9178-010705925a5d
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Interactive Discord Components Implemented Extending View

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISCORD-001** MUST: Interactive Discord components MUST be implemented by extending discord.ui.View, discord.ui.Select, discord.ui.Button, or modal base classes rather than constructing manual Discord API interaction payloads.

### Verify

```bash
# Discover and execute repository unit and integration test runners targeting the Discord adapter module suite
pytest tests/adapters/discord/

# Run repository static analysis and linting tools to confirm compliant import usage and rule adherence across all adapter components
flake8 src/adapters/discord/
mypy src/adapters/discord/
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites, static analysis linters, and peer code reviews verify rule compliance.
</enforcement>