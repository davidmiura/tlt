# Discord Library Adoption for Bot Adapter Architecture: Discord Adapter Subsystem Adopt Library Primary

These rules are ALWAYS ACTIVE for all modules, command handlers, UI views, moderation enforcers, and tasks within the Discord adapter subsystem.

### Rules

- **R-DISCORD-001** MUST: The Discord adapter subsystem MUST adopt the discord library as the primary integration framework for handling Discord Gateway events, command interactions, UI components, and background tasks.
- **R-DISCORD-002** MUST: Pin exact dependency versions in repository lock files and isolate discord library types inside the adapter module boundary.
- **R-DISCORD-003** MUST: Enforce strict module boundaries via automated static analysis and translate Discord interaction payloads into internal domain DTOs within adapter handlers.

### Verify

```bash
# Discover and run static analysis verification to ensure discord imports remain restricted to the adapter boundary
# Discover and run the repository test suite to validate command handlers, UI view callbacks, and scheduled tasks
```

**Accept when:**
- Static analysis confirms all Discord interactions, UI views, and background tasks conform to discord library contracts within the adapter layer.
- Test suite passes all unit and integration specifications for command handling, UI modal interactions, and background task loops without leaking platform types across subsystem boundaries.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis and continuous integration test suites verify compliance with module import boundaries, UI view inheritance, and interaction response conventions.
</enforcement>