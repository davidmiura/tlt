# FastAPI Web Framework Adoption: Expose Dedicated Health Status Endpoints Every

These rules are ALWAYS ACTIVE for all backend service and adapter modules that expose HTTP interfaces, ingest webhook events, or provide operational endpoints.

### Rules

- **R-FASTAPI-001** MUST: Expose dedicated health status endpoints on every network-facing service component to support operational monitoring and liveness probes.

### Verify

```bash
# Discover dependency manifest/lock and verify the web framework dependency
# Discover and execute static analysis and linting commands for asynchronous endpoint patterns
# Run integration test suites across all registered HTTP route modules
```

**Accept when:**
- All service HTTP routes and modular routers import and instantiate the adopted framework without alternative HTTP library imports.
- The project dependency verification script confirms the resolved locked framework version matches the deployed environment.
- Automated endpoint test suites pass with non-blocking asynchronous request execution across all service modules.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>