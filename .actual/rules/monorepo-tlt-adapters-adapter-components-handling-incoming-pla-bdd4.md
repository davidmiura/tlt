# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Adapter Components Handling Incoming Platform Interactions

These rules are ALWAYS ACTIVE for all adapter components handling incoming platform interactions, commands, guild operations, and runtime health checks within the Discord adapter package.

### Rules

- **R-DISC-001** MUST: All adapter components handling incoming platform interactions, commands, guild operations, and runtime health checks MUST coordinate state, authorization, and lifecycle management exclusively through the tlt.adapters.discord_adapter.bot_manager module.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager.
# Discover and execute the repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures.
pytest -k "discord_adapter"
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates.
</enforcement>