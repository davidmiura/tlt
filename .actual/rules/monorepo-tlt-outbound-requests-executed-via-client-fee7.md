# Requests Library Adoption for Synchronous HTTP Operations: Outbound Requests Executed Via Client Explicitly

These rules are ALWAYS ACTIVE for all synchronous outbound HTTP requests executed across service boundaries and external service connectivity validation and resource download tasks in worker processes.

### Rules

- **R-REQ-001** MUST: All outbound requests executed via the client MUST explicitly specify a timeout parameter to prevent indefinite thread blocking on network operations.

### Verify

```bash
# Discover and execute the project static analysis suite to verify that all external HTTP invocations supply an explicit timeout argument.
# Discover and run the project test runner to execute unit and integration test suites validating external client error handling and response parsing.
```

**Accept when:**
- All synchronous outbound HTTP invocations specify an explicit timeout parameter.
- Project test suites mocking external HTTP client responses pass without unhandled network exceptions.
- Repository lock artifact inspection confirms the resolved HTTP client version satisfies project dependency constraints.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>