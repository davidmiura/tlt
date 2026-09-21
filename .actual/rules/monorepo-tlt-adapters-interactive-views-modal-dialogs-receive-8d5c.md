# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Interactive Views Modal Dialogs Receive Bot

These rules are ALWAYS ACTIVE for all command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package, and any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

### Rules

- **R-DISC-001** SHOULD: Interactive UI views and modal dialogs SHOULD receive the bot manager instance through constructor injection to facilitate delegation and lifecycle continuity across interaction flows.
- **R-DISC-002** MANDATORY: The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-DISC-003** MANDATORY: Before writing code that uses a versioned library, execute in order: (1) Find the dependency manifest, (2) Identify the build tool, (3) Inspect the repository lock or resolution artifact, (4) Look up official documentation for that exact version, (5) Confirm every API/class/function exists in that exact version, (6) Re-run steps 3-5 per dependency at point of use.
- **R-DISC-004** MANDATORY: Construct handlers and views with explicit bot manager injection rather than relying on module-level global lookups where possible.
- **R-DISC-005** MANDATORY: Validate that all command responses handle ephemeral interaction expirations gracefully during downstream processing.

### Verify

```bash
# Discover and run the project test suite to verify adapter command and view integration against the bot manager.
# Discover and execute repository static analysis tooling to verify adapter modules conform to bot manager contract signatures.
```

**Accept when:**
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

<enforcement>
Verified by: Continuous integration test suites validating command, view, and moderation interactions against mock bot manager instances, and peer code review. Pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates. Architectural violations must be remediated by refactoring handlers to accept and query the central bot manager instance. Exceptions for standalone administrative utilities or stateless webhooks require written architectural review and sign-off documenting alternate state handling.
</enforcement>