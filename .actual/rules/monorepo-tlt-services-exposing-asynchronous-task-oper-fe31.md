# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Services Exposing Asynchronous Task Operations Implement

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-TASK-001** MUST: Services exposing asynchronous task operations MUST implement data access routes using FastAPI APIRouter instances with dedicated endpoints for batch submission, task result retrieval, task cancellation, and service health inspection.

### Verify

```bash
echo "Discover and execute the repository test runner targeting task lifecycle API route test suites"
echo "Discover and execute the repository static analysis and type checking tools against routing modules"
```

**Accept when:**
- All unit and integration tests for batch submission, result retrieval, and cancellation endpoints pass successfully.
- Static analysis validates that route handlers enforce maximum batch limits and return typed response schemas.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>