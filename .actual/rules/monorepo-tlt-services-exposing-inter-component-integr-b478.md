# FastAPI Service Boundary Integration and Health Probe Routing: Services Exposing Inter Component Integration Interfaces

These rules are ALWAYS ACTIVE for all inter-service HTTP communication boundaries, external adapter integration endpoints, and service health/readiness probe implementations.

### Rules

- **R-FAST-001** MUST: Services exposing inter-component integration interfaces MUST define their boundary contracts using FastAPI APIRouter instances that separate boundary routing from core business logic.

### Verify

```bash
# Discover the project test execution script and run the integration test suite targeting service routers and health probe endpoints
# Discover the service configuration verification script and execute dependency reachability checks against all configured endpoints
```

**Accept when:**
- All integration test suites targeting router endpoints and health probes execute to completion with zero failures.
- Service readiness and liveness endpoints respond with successful HTTP status codes and valid operational payload dictionaries.
- Boundary contract tests confirm that invalid or malformed incoming payloads are rejected with appropriate error responses.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests lacking required health probes or router integration contracts are blocked from merging, and unvalidated endpoint schemas detected during automated verification trigger build failures requiring immediate remediation.
</enforcement>