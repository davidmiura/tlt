# FastAPI Asynchronous Task Lifecycle Data Access Pattern: Route Handlers Verify Availability Downstream Task

These rules are ALWAYS ACTIVE for HTTP-accessible service endpoints responsible for asynchronous task dispatch, status polling, and lifecycle cancellation, and service routing modules integrating with background execution managers.

### Rules

- **R-TASK-001** MUST: Route handlers MUST verify the availability of the downstream task execution manager prior to processing and raise an HTTPException with status code 503 when the manager is uninitialized.

### Verify

```bash
# Discover and execute the repository test runner targeting task lifecycle API route test suites
# Discover and execute the repository static analysis and type checking tools against routing modules
```

**Accept when:**
- All unit and integration tests for batch submission, result retrieval, and cancellation endpoints pass successfully.
- Static analysis validates that route handlers enforce maximum batch limits and return typed response schemas.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration test suites, static analysis, and peer code reviews verify rule compliance.
</enforcement>