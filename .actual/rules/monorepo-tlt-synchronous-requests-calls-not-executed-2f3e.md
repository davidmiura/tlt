# Requests Library Adoption for Synchronous HTTP Operations: Synchronous Requests Calls Not Executed Directly

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-REQ-001** MUST_NOT: Synchronous requests calls MUST NOT be executed directly within asynchronous event loops where blocking operations degrade event loop throughput.

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
Claude Code MUST NOT skip or defer verification. All external HTTP invocations must be statically checked for explicit timeouts and verified against network boundary rules.
</enforcement>