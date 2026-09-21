# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Health Check Route Handlers Distinguish Between

These rules are ALWAYS ACTIVE for HTTP service boundary entrypoints, modular domain routers exposing operational or task execution endpoints, and subsystems requiring external readiness and liveness inspection.

### Rules

- **R-HLTH-001** SHOULD: Health check route handlers SHOULD distinguish between nominal, degraded, and failed states based on subsystem responsiveness and queue backlog metrics.
- **R-HLTH-002** MANDATORY: The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-HLTH-003** MANDATORY: Before writing code that uses a versioned library, execute lock-version grounding: find dependency manifest, identify build tool, inspect repository lock/resolution artifact, look up official documentation for that exact version, confirm API existence, and re-run per dependency at point of use.
- **R-HLTH-004** MANDATORY: Health check route handlers must be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.
- **R-HLTH-005** SHOULD: Subsystem readiness checks should aggregate critical runtime metrics such as queue size and task processing state into the response body.

### Verify

```bash
shell_cmd=
$SHELL -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'
$SHELL -c 'grep -rE "@(app|router)\.get\(\"/health" .'
```

**Accept when:**
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>