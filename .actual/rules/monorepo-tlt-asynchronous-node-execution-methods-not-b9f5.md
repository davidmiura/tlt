# asyncio Standard Library Module: Asynchronous Node Execution Methods Not Execute

These rules are ALWAYS ACTIVE for event-driven agent nodes, background task monitors, service communication handlers, and service proxy gateways requiring asynchronous I/O.

### Rules

- **R-ASYNC-001** MUST_NOT: Asynchronous node execution methods MUST NOT execute blocking synchronous I/O operations directly on the primary event loop thread.
- **R-ASYNC-002** EXCEPTION: A third-party client library provides only synchronous interfaces and must be wrapped in an executor (EXC-20-001).

### Verify

```bash
# Discover the project test execution runner from repository configuration and execute the asynchronous test suite.
# Identify the static analysis and type verification script from workspace metadata and run verification across all modules.
```

**Accept when:**
- All asynchronous test suites pass with zero unhandled coroutine warnings or unawaited task errors.
- Static analysis confirms no synchronous blocking calls exist within asynchronous node execution methods.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>