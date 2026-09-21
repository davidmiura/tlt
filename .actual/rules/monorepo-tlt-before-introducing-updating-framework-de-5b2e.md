# FastAPI Service Boundary Integration and Health Probe Routing: Before Introducing Updating Framework Dependencies Engineers

These rules are ALWAYS ACTIVE for all inter-service HTTP communication boundaries, external adapter integration endpoints, and service health/readiness probe implementations within the distributed application architecture.

### Rules

- **R-ADR-001** MUST: Before introducing or updating framework dependencies, engineers MUST inspect the project dependency lock artifact to confirm the exact resolved version and verify that all invoked routing interfaces exist in that version reference documentation.

### Verify

```bash
# Discover and run the project integration test suite targeting service routers and health probe endpoints
# Discover and execute the service configuration verification script to check dependency reachability against configured endpoints
```

**Accept when:**
- All integration test suites targeting router endpoints and health probes execute to completion with zero failures.
- Service readiness and liveness endpoints respond with successful HTTP status codes and valid operational payload dictionaries.
- Boundary contract tests confirm that invalid or malformed incoming payloads are rejected with appropriate error responses.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration pipelines, peer code reviews, and automated verification runs enforce these boundary contracts and lock artifact inspection rules.
</enforcement>