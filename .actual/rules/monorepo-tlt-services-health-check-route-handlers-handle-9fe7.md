# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Health Check Route Handlers Handle Internal

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-OBS-001** MUST: Health check route handlers MUST handle internal subsystem exceptions gracefully, logging failure details via the structured logger and returning an explicit failure payload or status code.
- **R-OBS-002** MUST: Health check route handlers MUST be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.

### Verify

```bash
SHELL_CMD=${SHELL:-sh}
$SHELL_CMD -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'
$SHELL_CMD -c 'grep -rE "@(app|router)\.get\(\"/health" .'
```

**Accept when:**
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>