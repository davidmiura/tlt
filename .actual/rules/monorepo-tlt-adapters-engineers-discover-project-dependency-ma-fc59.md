# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Engineers Discover Project Dependency Manifest Lock

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, as well as any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISCORD-001** MUST: Engineers MUST discover the project dependency manifest and lock artifact to resolve the exact locked version of all underlying platform libraries and runtime dependencies before implementation, verifying that all invoked interfaces conform to version-specific documentation.
- **R-DISCORD-002** MUST: Construct handlers and views with explicit bot manager injection rather than relying on module-level global lookups where possible.
- **R-DISCORD-003** MUST: Validate that all command responses handle ephemeral interaction expirations gracefully during downstream processing.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager
# Discover and execute the repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Claude Code MUST NOT skip or defer verification. All adapter command handlers, views, and event enforcers must be verified against mock bot manager instances, and pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked.
</enforcement>