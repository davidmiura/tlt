# discord Library UI Modal and Interaction Handler Adoption: Modal Classes Not Execute Domain Persistence

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** MUST: Modal classes MUST NOT execute domain persistence or business logic directly within the asynchronous on_submit callback.

### Verify

```bash
# Discover and run the repository dependency verification command
# Discover and run the repository test runner script covering adapter modal classes and submission handlers
# Discover and run the repository static analysis linter against adapter command and event bridge packages
```

**Accept when:**
- All modal user input interactions subclass the discord UI modal base class and delegate submission payloads to dedicated interaction handlers.
- Static analysis and test suites verify that modal callback methods contain no direct persistence or business domain logic.
- The project dependency lock artifact is inspected and verified prior to consuming discord UI component APIs.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis, continuous integration test suites, and peer code review enforce handler delegation within modal callbacks, blocking PRs containing business domain logic inside modal UI classes.
</enforcement>