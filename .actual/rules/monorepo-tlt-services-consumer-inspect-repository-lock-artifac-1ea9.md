# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Consumer Inspect Repository Lock Artifact Determine

These rules are ALWAYS ACTIVE for HTTP service boundary entrypoints, modular domain routers, and subsystems requiring external readiness and liveness inspection.

### Rules

- **R-HLTH-001** MUST: The consumer MUST inspect the repository lock artifact to determine the exact resolved version of the framework dependency before implementing route handlers or response contracts.
- **R-HLTH-002** MUST: Health check route handlers must be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.
- **R-HLTH-003** SHOULD: Subsystem readiness checks should aggregate critical runtime metrics such as queue size and task processing state into the response body.

### Verify

```bash
# Verify test runner discovery
$SHELL -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'

# Verify health check route registrations
$SHELL -c 'grep -rE "@(app|router)\.get\(\"/health" .'
```

**Accept when:**
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests missing health check routes on new HTTP services or routers will fail review approval, and build failures will be triggered by missing or broken readiness endpoints during integration testing.
</enforcement>