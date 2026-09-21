# discord Library UI Modal and Interaction Handler Adoption: Before Implementing Updating Components Discord Library

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-DISC-001** MUST: Before implementing or updating components using the discord library, the consumer MUST inspect the project lock or resolution artifact to determine the exact resolved dependency version and verify API compatibility against that version.
- **R-DISC-002** MUST: All modal user input interactions subclass the discord UI modal base class and delegate submission payloads to dedicated interaction handlers.
- **R-DISC-003** MUST: Instantiate submission handlers with necessary runtime bot instances during modal submission callbacks rather than retaining long-lived cyclic references in UI components.
- **R-DISC-004** MUST: Maintain typed input field value extraction at the modal boundary before dispatching clean primitive or domain arguments to the handling layer.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>