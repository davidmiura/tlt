# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Health Check Route Handlers Probe Internal

These rules are ALWAYS ACTIVE for all FastAPI HTTP service boundary entrypoints, modular domain routers exposing operational or task execution endpoints, and subsystems requiring external readiness and liveness inspection.

### Rules

- **R-HLTH-001** MUST: Health check route handlers MUST probe internal runtime subsystem status and return structured payloads containing operational status indicators.
- **R-HLTH-002** MUST: Health check route handlers must be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.

### Verify

```bash
# $SHELL -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'
# $SHELL -c 'grep -rE "@(app|router)\.get\(\"/health" .'
```

**Accept when:**
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>