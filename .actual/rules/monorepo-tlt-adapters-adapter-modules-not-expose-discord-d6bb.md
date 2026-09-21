# Discord Library Adoption for Bot Adapter Architecture: Adapter Modules Not Expose Discord Library

These rules are ALWAYS ACTIVE for all modules, command handlers, UI views, moderation enforcers, tasks, and inbound/outbound communication interfaces within the Discord adapter subsystem.

### Rules

- **R-DISC-001** MUST_NOT: Adapter modules MUST NOT expose discord library types or raw interaction payloads outside the adapter subsystem boundary.

### Verify

```bash
# Discover and run the project static analysis verification to ensure discord imports remain restricted to the adapter boundary
# Discover and run the repository test suite to validate command handlers, UI view callbacks, and scheduled tasks
```

**Accept when:**
- Static analysis confirms all Discord interactions, UI views, and background tasks conform to discord library contracts within the adapter layer.
- Test suite passes all unit and integration specifications for command handling, UI modal interactions, and background task loops without leaking platform types across subsystem boundaries.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification of module import boundaries and continuous integration test suites is mandatory.
</enforcement>