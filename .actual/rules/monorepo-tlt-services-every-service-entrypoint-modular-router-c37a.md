# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Every Service Entrypoint Modular Router Expose

These rules are ALWAYS ACTIVE for all FastAPI service entrypoints and modular domain routers exposing operational or task execution endpoints.

### Rules

- **R-OBS-001** MUST: Every service entrypoint and modular router MUST expose an asynchronous health check endpoint decorated with the framework route decorator for the standard health path.
- **R-OBS-002** MUST: Health check route handlers must be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.
- **R-OBS-003** SHOULD: Subsystem readiness checks aggregate critical runtime metrics such as queue size and task processing state into the response body.

### Verify

```bash
$SHELL -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'
$SHELL -c 'grep -rE "@(app|router)\.get\(\"/health" .'
```

**Accept when:**
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests missing health check routes on new HTTP services or routers will fail review approval, and build failures will be triggered by missing or broken readiness endpoints during integration testing.
</enforcement>