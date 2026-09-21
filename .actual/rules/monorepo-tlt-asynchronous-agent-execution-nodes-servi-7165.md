# asyncio Standard Library Module: Asynchronous Agent Execution Nodes Service Interface

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ASYNC-001** MUST: Asynchronous agent execution nodes and service interface handlers MUST use the standard asyncio module primitives to implement non-blocking coroutines and event-driven control flow.

### Verify

```bash
# Discover the project test execution runner from repository configuration and execute the asynchronous test suite.
# Identify the static analysis and type verification script from workspace metadata and run verification across all modules.
```

**Accept when:**
- All asynchronous test suites pass with zero unhandled coroutine warnings or unawaited task errors.
- Static analysis confirms no synchronous blocking calls exist within asynchronous node execution methods.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>