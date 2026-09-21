# FastAPI Web Framework Adoption: Adopt Fastapi Framework Standard Asynchronous Web

These rules are ALWAYS ACTIVE for all backend service and adapter modules that expose HTTP interfaces, ingest webhook events, or provide operational endpoints.

### Rules

- **R-FASTAPI-001** MUST: Adopt the FastAPI framework as the standard asynchronous web application framework for exposing HTTP endpoints and modular routing across service components.
- **R-FASTAPI-002** MUST: Follow the lock-version grounding policy (discover dependency manifest, identify build tool, inspect repository lock or resolution artifact, look up official documentation, confirm API existence) before writing code that uses a versioned library.
- **R-FASTAPI-003** MUST: Instantiate service applications at designated service entry points and mount modular sub-routers using prefix paths and tags.
- **R-FASTAPI-004** MUST: Keep route handlers thin by offloading business logic and background processing directly to asynchronous task managers.

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
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>