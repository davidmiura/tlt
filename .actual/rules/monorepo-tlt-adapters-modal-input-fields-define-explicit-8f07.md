# discord Library UI Modal and Interaction Handler Adoption: Modal Input Fields Define Explicit Validation

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** SHOULD: Modal input fields SHOULD define explicit validation constraints including required flags and maximum length limits at the component boundary.
- **R-MOD-002** MANDATORY (Discovery Policy): The consumer MUST derive tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-MOD-003** MANDATORY (Lock-Version Grounding): Before writing code that uses a versioned library, execute in order: find dependency manifest, identify build tool, inspect repository lock or resolution artifact for exact resolved version, look up official documentation for that exact version, confirm every API/class/function exists in that version, re-run per dependency at point of use.

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
Claude Code MUST NOT skip or defer verification. All modal user input interactions and handler delegations are strictly verified by automated static analysis, linters, test suites, and peer code review.
</enforcement>