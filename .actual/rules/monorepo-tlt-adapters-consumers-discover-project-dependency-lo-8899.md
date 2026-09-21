# Discord Interaction Handling via Ephemeral Response Messaging: Consumers Discover Project Dependency Lock Artifact

These rules are ALWAYS ACTIVE for all Discord adapter command handlers, interaction callbacks, user interface views, and modals processing incoming guild and user events.

### Rules

- **R-DISCORD-001** MUST: Consumers MUST discover the project dependency lock artifact and verify the exact resolved version of the discord library before implementing or modifying interaction handlers.

### Verify

```bash
# Discover and execute project test suite runner
# Discover and execute project static analysis and linting verification scripts
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>