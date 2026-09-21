# discord Library UI Modal and Interaction Handler Adoption: Submit Callback Discord Modal Delegate Input

These rules are ALWAYS ACTIVE for interactive user input collection forms within platform adapter command modules and event bridge handlers processing structured modal submission interactions.

### Rules

- **R-DISCORD-001** MUST: The on_submit callback of a discord.ui.Modal MUST delegate input processing to a dedicated handler instance via an asynchronous handle_modal_submission invocation passing the interaction context and field values.

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
Claude Code MUST NOT skip or defer verification. Automated static analysis rules, linters, continuous integration automated test suites, and peer code reviews enforce these requirements.
</enforcement>