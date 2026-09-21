# Discord Interaction Handling via Ephemeral Response Messaging: Handlers Validate User Permissions Guild Registration

These rules are ALWAYS ACTIVE for Discord adapter command handlers, interaction callbacks, and user interface views processing incoming guild and user events.

### Rules

- **R-DISC-001** MUST: Handlers MUST validate user permissions and guild registration against the bot manager before delegating mutations to backend integration clients.

### Verify

```bash
# Discover and execute the project test suite runner to validate adapter interaction handler compliance.
# Discover and execute the project static analysis and linting verification scripts to check interaction response configurations.
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>