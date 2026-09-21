# Requests Library Adoption for Synchronous HTTP Operations: Modules Executing Synchronous Outbound Http Communications

These rules are ALWAYS ACTIVE for modules executing synchronous outbound HTTP communications or external service connectivity checks.

### Rules

- **R-REQ-001** MUST: Modules executing synchronous outbound HTTP communications or external service connectivity checks MUST standardize on the requests library as the baseline client.

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