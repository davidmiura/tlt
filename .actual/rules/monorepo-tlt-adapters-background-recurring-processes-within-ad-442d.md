# Discord Library Adoption for Bot Adapter Architecture: Background Recurring Processes Within Adapter Use

These rules are ALWAYS ACTIVE for all modules, command handlers, UI views, moderation enforcers, and tasks within the Discord adapter subsystem.

### Rules

- **R-DISCORD-001** MUST: Background recurring processes within the adapter MUST use discord.ext task primitives to bind execution lifecycles to the bot connection state.

### Verify

```bash
# Discover and run the project static analysis verification to ensure discord imports remain restricted to the adapter boundary.
# Discover and run the repository test suite to validate command handlers, UI view callbacks, and scheduled tasks.
```

**Accept when:**
- Static analysis confirms all Discord interactions, UI views, and background tasks conform to discord library contracts within the adapter layer.
- Test suite passes all unit and integration specifications for command handling, UI modal interactions, and background task loops without leaking platform types across subsystem boundaries.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>