# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Adapter Submodules Not Instantiate Secondary Bot

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, and any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISCORD-001** MUST_NOT: Adapter submodules MUST_NOT instantiate secondary bot clients or bypass the bot manager to maintain uncoordinated connections to external messaging platform gateways.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager.
# Discover and execute the repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures.
pytest -k "discord or adapter"
ruff check . && mypy .
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via CI test suites and peer code reviews ensuring handlers consume the bot manager rather than instantiating external platform clients.
</enforcement>