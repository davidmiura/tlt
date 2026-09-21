# asyncio Standard Library Module: Engineers Verify Repository Dependency Manifest Lock

These rules are ALWAYS ACTIVE for event-driven agent processing nodes, background task monitors, service communication handlers, and service proxy gateways requiring asynchronous I/O.

### Rules

- **R-ASYNC-001** MUST: Engineers MUST verify the repository dependency manifest and lock artifact to ensure runtime environment compatibility before implementing asynchronous module extensions.

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