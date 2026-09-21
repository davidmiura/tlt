# asyncio Standard Library Module: Long Running Computational Tasks Blocking Calls

These rules are ALWAYS ACTIVE for event-driven agent nodes, background task monitors, service communication handlers requiring asynchronous I/O, service proxy gateways, and non-blocking interface adapters.

### Rules

- **R-ASYNC-001** SHOULD: Long-running computational tasks or blocking calls SHOULD be delegated to separate execution workers or asynchronous thread executors to preserve event loop responsiveness.

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