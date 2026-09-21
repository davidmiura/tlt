# FastAPI Service Boundary Integration and Health Probe Routing: Service Routers Expose Auxiliary Diagnostic Endpoints

These rules are ALWAYS ACTIVE for all inter-service HTTP communication boundaries, external adapter integration endpoints, and service health/readiness probe implementations.

### Rules

- **R-SF-039-001** MAY: Service routers MAY expose auxiliary diagnostic endpoints detailing supported event schema types, processing metrics, and queue operational capacities.

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
Claude Code MUST NOT skip or defer verification. Verification by continuous integration pipeline executing automated integration test suites, contract validation runs, and peer code review is mandatory.
</enforcement>