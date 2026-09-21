# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Active Event State Tracking Message Lookups

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, and any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISC-001** MUST: Active event state tracking, message lookups, and guild configurations MUST be read from and persisted to the bot manager state dictionaries rather than maintaining independent local caches.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager.
# Discover and execute repository static analysis tooling to verify adapter modules conform to bot manager contract signatures.
pytest -k "discord or adapter"
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. Pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates.
</enforcement>