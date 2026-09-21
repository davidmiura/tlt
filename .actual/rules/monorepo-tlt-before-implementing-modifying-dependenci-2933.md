# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Before Implementing Modifying Dependencies Task Lifecycle

These rules are ALWAYS ACTIVE for HTTP-accessible service endpoints responsible for asynchronous task dispatch, status polling, and lifecycle cancellation, and service routing modules integrating with background execution managers.

### Rules

- **R-TLT-001** MUST: Before implementing or modifying dependencies for task lifecycle routing, the engineer MUST inspect the repository lock artifact to determine the exact resolved dependency version and verify that all invoked API interfaces exist in that version reference.

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