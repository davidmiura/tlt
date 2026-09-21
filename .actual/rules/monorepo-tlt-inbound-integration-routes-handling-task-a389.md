# FastAPI Service Boundary Integration and Health Probe Routing: Inbound Integration Routes Handling Task Submission

These rules are ALWAYS ACTIVE for all inter-service HTTP communication boundaries, external adapter integration endpoints receiving asynchronous event signals or batch workloads, and service health and readiness probe implementations.

### Rules

- **R-FASTAPI-001** MUST: Inbound integration routes handling task submission or event delivery MUST validate incoming payloads against typed schemas and return structured status dictionaries confirming receipt and task identifier tracking.

### Verify

```bash
# Discover the project test execution script and run the integration test suite targeting service routers and health probe endpoints.
# Discover the service configuration verification script and execute dependency reachability checks against all configured endpoints.
```

**Accept when:**
- All integration test suites targeting router endpoints and health probes execute to completion with zero failures.
- Service readiness and liveness endpoints respond with successful HTTP status codes and valid operational payload dictionaries.
- Boundary contract tests confirm that invalid or malformed incoming payloads are rejected with appropriate error responses.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration pipeline automated integration test suites, contract validation runs, and peer code reviews verify compliance. Pull requests lacking required health probes or router integration contracts, or unvalidated endpoint schemas, trigger build failures or are blocked from merging.
</enforcement>