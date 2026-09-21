# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Task Response Structures Validated Serialized Through

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-TASK-001** SHOULD: Task response structures SHOULD be validated and serialized through Pydantic data models enforcing schema integrity across boundary contracts.

### Verify

```bash
# Discover and execute the repository test runner targeting task lifecycle API route test suites
# Discover and execute the repository static analysis and type checking tools against routing modules
```

**Accept when:**
- All unit and integration tests for batch submission, result retrieval, and cancellation endpoints pass successfully.
- Static analysis validates that route handlers enforce maximum batch limits and return typed response schemas.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>