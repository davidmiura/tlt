# discord Library UI Modal and Interaction Handler Adoption: Interactive Structured Input Dialogs Platform Adapter

These rules are ALWAYS ACTIVE for all platform adapter command modules, interactive user input collection forms, and event bridge handlers processing structured modal submission interactions.

### Rules

- **R-DISCORD-001** MUST: Interactive structured input dialogs in the platform adapter MUST subclass discord.ui.Modal and declare user input fields using discord.ui.TextInput components.

### Verify

```bash
# Discover and run repository dependency verification command
# Discover and run repository test runner script covering adapter modal classes and submission handlers
# Discover and run repository static analysis linter against adapter command and event bridge packages
```

**Accept when:**
- All modal user input interactions subclass the discord UI modal base class and delegate submission payloads to dedicated interaction handlers.
- Static analysis and test suites verify that modal callback methods contain no direct persistence or business domain logic.
- The project dependency lock artifact is inspected and verified prior to consuming discord UI component APIs.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis, continuous integration test suites, and peer code reviews enforce handler delegation within modal callbacks, blocking PRs that violate this rule.
</enforcement>