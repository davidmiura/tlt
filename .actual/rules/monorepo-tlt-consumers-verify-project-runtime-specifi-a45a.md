# asyncio Asynchronous Concurrency Architecture: Consumers Verify Project Runtime Specification Resolved

These rules are ALWAYS ACTIVE for all message adapter handlers, network endpoint routers, agent state execution workflow nodes, and background event monitoring loops.

### Rules

- **R-ASYNC-001** MUST: Consumers MUST verify the project runtime specification and resolved dependency resolution artifacts to ground concurrency APIs against active environment documentation before implementing coroutine interfaces.

### Verify

```bash
# Discover and run the project static analysis test suite to verify coroutine definitions and identify any unawaited calls
# Discover and execute the automated integration test suite to validate asynchronous event propagation across agent nodes
```

**Accept when:**
- All coroutines defined across event monitoring, routing, and adapter modules execute asynchronously without blocking the event loop
- Static concurrency verification verifies zero unawaited coroutine definitions across all service boundaries
- Automated test runs confirm that background tasks and scheduled timers process concurrently under active workloads

<enforcement>
Claude Code MUST NOT skip or defer verification. All network, file, and timer interactions must utilize non-blocking asynchronous APIs and be validated via continuous integration and peer code reviews.
</enforcement>