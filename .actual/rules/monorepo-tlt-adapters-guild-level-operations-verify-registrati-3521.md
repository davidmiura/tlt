# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Guild Level Operations Verify Registration Status

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, and any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISCORD-001** MUST: Guild-level operations MUST verify guild registration status using the bot manager is_guild_registered method prior to executing event creation, updates, deletions, or status inquiries.

### Verify

```bash
# Discover and run project test suite to verify adapter command and view integration against the bot manager
# Discover and execute repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates.
</enforcement>