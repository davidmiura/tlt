# Discord Interaction Handling via Ephemeral Response Messaging: Integration Error Responses Generated During Command

These rules are ALWAYS ACTIVE for all Discord adapter command handlers and interaction callbacks processing incoming guild and user events, including user interface views and modals handling interaction events within the chat adapter boundary.

### Rules

- **R-DISCORD-001** MUST_NOT: Integration error responses generated during command handling MUST NOT expose raw internal exceptions or sensitive server metadata to interaction responses.

### Verify

```bash
# Discover and execute the project test suite runner to validate adapter interaction handler compliance.
# Discover and execute the project static analysis and linting verification scripts to check interaction response configurations.
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration test suites and peer review validate interaction handler response flags and exception handling.
</enforcement>