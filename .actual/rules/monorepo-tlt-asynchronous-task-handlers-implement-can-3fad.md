# asyncio Standard Library Module: Asynchronous Task Handlers Implement Cancellation Tokens

These rules are ALWAYS ACTIVE for event-driven agent processing nodes, background task monitors, service communication handlers requiring asynchronous I/O, service proxy gateways, and non-blocking interface adapters.

### Rules

- **R-ASYNC-001** MAY: Asynchronous task handlers MAY implement cancellation tokens and cooperative yield points to support clean shutdown and state persistence during service interruption.

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