# Discord Interaction Handling via Ephemeral Response Messaging: Command Handlers Encapsulate Multi Step Mutation

These rules are ALWAYS ACTIVE for all Discord adapter command handlers and interaction callbacks processing incoming guild and user events, as well as user interface views and modals handling interaction events within the chat adapter boundary.

### Rules

- **R-DISCORD-001** SHOULD: Command handlers SHOULD encapsulate multi-step mutation confirmations within dedicated modal classes before executing state modifications.

### Verify

```bash
# Discover and execute project test suite and linting verification scripts
# (Commands to be discovered from project repository manifest/scripts)
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via continuous integration test suites and peer review.
</enforcement>