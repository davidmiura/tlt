# FastAPI Web Framework Adoption: Execute Blocking Synchronous Operations Prolonged Compute

These rules are ALWAYS ACTIVE for all backend service and adapter modules that expose HTTP interfaces, ingest webhook events, or provide operational endpoints.

### Rules

- **R-FASTAPI-001** MUST_NOT: Execute blocking synchronous operations or prolonged compute-heavy workflows directly inside asynchronous route handler functions.

### Verify

```bash
# Discover the repository dependency manifest and lock file, and verify that the web framework dependency is locked and matches the installed environment.
# Discover and execute the repository static analysis and linting commands to confirm compliance with asynchronous endpoint patterns.
# Discover and run the project integration test suite across all registered HTTP route modules.
```

**Accept when:**
- All service HTTP routes and modular routers import and instantiate the adopted framework without alternative HTTP library imports.
- The project dependency verification script confirms the resolved locked framework version matches the deployed environment.
- Automated endpoint test suites pass with non-blocking asynchronous request execution across all service modules.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>