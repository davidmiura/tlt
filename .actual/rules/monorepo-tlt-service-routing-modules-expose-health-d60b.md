# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Service Routing Modules Expose Health Check

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-TLT-001** SHOULD: Service routing modules SHOULD expose a health check route returning operational status, downstream execution manager availability, and an inventory of supported task lifecycle endpoints.

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