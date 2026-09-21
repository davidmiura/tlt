# FastAPI Service Boundary Integration and Health Probe Routing: Integration Route Handlers Not Perform Direct

These rules are ALWAYS ACTIVE for all inter-service HTTP communication boundaries, external adapter integration endpoints, and service health/readiness probe implementations within the distributed application architecture.

### Rules

- **R-INTEG-001** MUST_NOT: Integration route handlers MUST_NOT perform direct in-process blocking operations and MUST hand off long-running event processing to asynchronous queues or managers.

### Verify

```bash
# Discover and execute the project integration test suite targeting service routers and health probe endpoints
# Discover and execute the service configuration verification script to run dependency reachability checks
```

**Accept when:**
- All integration test suites targeting router endpoints and health probes execute to completion with zero failures.
- Service readiness and liveness endpoints respond with successful HTTP status codes and valid operational payload dictionaries.
- Boundary contract tests confirm that invalid or malformed incoming payloads are rejected with appropriate error responses.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests lacking required health probes or router integration contracts are blocked from merging, and unvalidated endpoint schemas detected during automated verification trigger build failures requiring immediate remediation.
</enforcement>