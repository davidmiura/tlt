# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Batch Task Submission Endpoints Iterate Over

These rules are ALWAYS ACTIVE for HTTP-accessible service endpoints responsible for asynchronous task dispatch, status polling, and lifecycle cancellation, and service routing modules integrating with background execution managers.

### Rules

- **R-TASK-001** MUST: Batch task submission endpoints MUST iterate over input items with isolated exception handling, capturing individual submission identifiers for successful items and error details for failed items in structured response accounting.

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