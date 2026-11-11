---
version: 2
name: cross-cutting-consumers-discover-ecosystem-dependency-f4bc
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Consumers Discover Ecosystem Dependency Manifest Authoritative"
metadata:
  actual:
    adr_id: f4bcc979-188d-4721-bc77-98e92c328dd0
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Consumers Discover Ecosystem Dependency Manifest Authoritative

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all modules and classes within the Discord adapter boundary interacting with the Discord Gateway, application commands, or user interface components, and scheduled background routines managing periodic checks or automated reminder broadcasts within the Discord client runtime.

### Rules

- **R-ADP-001** MUST: Consumers MUST discover the ecosystem dependency manifest and authoritative lock artifact to resolve the exact locked version of discord.py and verify all invoked APIs against that version's documentation prior to implementation.

### Verify

```bash
# Discover and execute repository test runners targeting the Discord adapter module suite
# Discover and run repository static analysis and linting tools to confirm compliant import usage
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites, continuous integration linters, and peer code reviews enforce module boundaries and direct interaction model compliance.
</enforcement>