# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Health Check Endpoints Not Perform Mutating

These rules are ALWAYS ACTIVE for HTTP service boundary entrypoints, modular domain routers exposing operational or task execution endpoints, and subsystems requiring external readiness and liveness inspection.

### Rules

- **R-HEALTH-001** MUST_NOT: Health check endpoints MUST NOT perform mutating state modifications or heavy computations that impact request processing throughput.

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
Claude Code MUST NOT skip or defer verification. Continuous integration test suites and static analysis checks must verify endpoint availability and status responses.
</enforcement>