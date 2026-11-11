---
version: 2
name: cross-cutting-domain-operations-business-services-deco-a9e5
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Domain Operations Business Services Decoupled Discord"
metadata:
  actual:
    adr_id: a9e5e9b6-e087-4eb8-8548-74f2808b7457
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Domain Operations Business Services Decoupled Discord

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISC-001** SHOULD: Domain operations and business services SHOULD be decoupled from Discord client state by delegating requests through dedicated bridge and handler abstractions.
- **R-DISC-002** MANDATORY: Maintain strict isolation between Discord UI elements such as views, selects, and modals and core domain service clients by delegating via bridge handlers.
- **R-DISC-003** MANDATORY: Ensure all interaction responses acknowledge user actions within platform latency limits to prevent expired interaction tokens.
- **R-DISC-004** MANDATORY: Structure slash commands within centralized command routers and register handlers asynchronously during client startup hooks.
- **R-DISC-005** MANDATORY (LOCK-VERSION GROUNDING): Before writing code that uses a versioned library, execute in order: (1) Find dependency manifest, (2) Identify build tool, (3) Inspect repository lock/resolution artifact for exact version, (4) Look up official docs for that exact version, (5) Confirm every API/class/function exists in that version, (6) Re-run at point of use for version-sensitive behavior.

### Verify

```bash
# Discover and execute repository unit and integration test runners targeting the Discord adapter module suite
# Discover and run repository static analysis and linting tools to confirm compliant import usage and rule adherence across all adapter components
```

**Accept when:**
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions.
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase.
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests introducing direct HTTP Discord requests or bypassing interaction models will be blocked by automated reviews.
</enforcement>