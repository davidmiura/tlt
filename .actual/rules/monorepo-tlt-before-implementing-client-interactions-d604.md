# Requests Library Adoption for Synchronous HTTP Operations: Before Implementing Client Interactions Developers Inspect

These rules are ALWAYS ACTIVE for all synchronous outbound HTTP requests executed across service boundaries, external service connectivity validation, and resource download tasks in worker processes.

### Rules

- **R-REQ-001** MUST: Before implementing client interactions, developers MUST inspect the repository lock or resolution artifact to determine the exact resolved version of the requests library and verify API compatibility against that specific version.
- **R-REQ-002** MUST: Always supply explicit timeout values representing connect and read limits on every network invocation.
- **R-REQ-003** SHOULD: When executing repetitive requests against the same remote host, instantiate and reuse a client session instance to benefit from connection pooling.

### Verify

```bash
# Discover and execute project static analysis and test suites
# (Commands must be discovered from repository configuration, e.g., pytest, tox, ruff, mypy)
```

**Accept when:**
- All synchronous outbound HTTP invocations specify an explicit timeout parameter.
- Project test suites mocking external HTTP client responses pass without unhandled network exceptions.
- Repository lock artifact inspection confirms the resolved HTTP client version satisfies project dependency constraints.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis and peer code review enforce these rules; non-compliant pull requests will be blocked.
</enforcement>