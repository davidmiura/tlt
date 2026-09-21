# Discord Library Adoption for Bot Adapter Architecture: Consumers Discover Inspect Repository Lock Artifact

These rules are ALWAYS ACTIVE for all modules, command handlers, UI views, moderation enforcers, and tasks within the Discord adapter subsystem.

### Rules

- **R-DISC-001** MUST: Consumers MUST discover and inspect the repository lock artifact to determine the exact locked version of the discord library before implementing or updating adapter components.
- **R-DISC-002** MUST: Follow lock-version grounding by finding the dependency manifest, identifying the build tool, inspecting the lock/resolution artifact, looking up official docs for that exact version, confirming API existence, and re-running per dependency at point of use.
- **R-DISC-003** MUST: Implement interactive user interface components by subclassing the standard view class and dispatching user input through dedicated modal and select callback handlers.
- **R-DISC-004** MUST: Coordinate Discord client lifecycle events and guild registration state through the central bot manager instance inside the adapter subsystem.

### Verify

```bash
# Discover and run static analysis verification to ensure discord imports remain restricted to the adapter boundary
# Discover and run the repository test suite to validate command handlers, UI view callbacks, and scheduled tasks
```

**Accept when:**
- Static analysis confirms all Discord interactions, UI views, and background tasks conform to discord library contracts within the adapter layer.
- Test suite passes all unit and integration specifications for command handling, UI modal interactions, and background task loops without leaking platform types across subsystem boundaries.

<enforcement>
Verification is mandatory. Claude Code MUST NOT skip or defer verification.
</enforcement>