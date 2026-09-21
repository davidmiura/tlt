# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Command Handlers Interactive Views Delegate Administrative

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, and any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISC-001** MUST: Command handlers and interactive UI views MUST delegate administrative authorization checks directly to the bot manager is_admin method rather than performing autonomous permission evaluations.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager.
pytest tests/adapters/discord_adapter/

# Discover and execute the repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures.
flake8 src/tlt/adapters/discord_adapter/
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates.
</enforcement>