# FastAPI Web Framework Adoption: Decompose Service Endpoint Groups Modular Apirouter

These rules are ALWAYS ACTIVE for all backend service and adapter modules that expose HTTP interfaces, ingest webhook events, or provide operational endpoints.

### Rules

- **R-FAP-001** MUST: Decompose service endpoint groups into modular APIRouter instances mounted onto the primary application instance rather than defining routes on a monolithic application object.

### Verify

```bash
# Discover dependency manifest and lock file, verify framework dependency
# Discover and execute repository static analysis and linting commands for async endpoint patterns
# Discover and run integration test suite across registered HTTP route modules
```

**Accept when:**
- All service HTTP routes and modular routers import and instantiate the adopted framework without alternative HTTP library imports.
- The project dependency verification script confirms the resolved locked framework version matches the deployed environment.
- Automated endpoint test suites pass with non-blocking asynchronous request execution across all service modules.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>