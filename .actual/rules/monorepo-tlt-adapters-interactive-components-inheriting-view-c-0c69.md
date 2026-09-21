# Discord Interaction Handling via Ephemeral Response Messaging: Interactive Components Inheriting View Classes Acknowledge

These rules are ALWAYS ACTIVE for Discord adapter command handlers, user interface views, and modals handling interaction events within the chat adapter boundary.

### Rules

- **R-DISCORD-001** MUST: Interactive UI components inheriting from view classes MUST acknowledge incoming interaction events within the timeout window via interaction response or modal submission methods.

### Verify

```bash
# Discover and execute the project test suite runner to validate adapter interaction handler compliance.
# Discover and execute the project static analysis and linting verification scripts to check interaction response configurations.
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests introducing non-ephemeral responses for validation, permission checks, or error paths will be blocked.
</enforcement>