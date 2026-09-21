# Requests Library Adoption for Synchronous HTTP Operations: Invocations Http Methods Encapsulate Calls Within

These rules are ALWAYS ACTIVE for all synchronous outbound HTTP requests executed across service boundaries, external service connectivity validation, and resource download tasks in worker processes.

### Rules

- **R-REQ-001** SHOULD: Invocations of HTTP methods SHOULD encapsulate calls within structured exception handling blocks to isolate network failures and client timeouts from caller workflows.
- **R-REQ-002** MANDATORY: Always supply explicit timeout values representing connect and read limits on every network invocation.
- **R-REQ-003** MANDATORY: When executing repetitive requests against the same remote host, instantiate and reuse a client session instance to benefit from connection pooling.

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