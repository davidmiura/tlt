# asyncio Asynchronous Concurrency Architecture: Event Handlers External Adapter Operations Agent

These rules are ALWAYS ACTIVE for all message adapter handlers, network endpoint routers, agent state execution workflow nodes, background event monitoring loops, scheduled timer evaluations, and asynchronous task dispatching pipelines.

### Rules

- **R-ASYNC-001** MUST: All event handlers, external adapter operations, agent execution nodes, and service endpoints MUST implement non-blocking coroutines using the adopted asyncio concurrency framework.
- **R-ASYNC-002** MUST: Utilize asynchronous queue primitives and non-blocking cooperative sleep functions for all polling loops and background agent cycles.
- **R-ASYNC-003** MUST: Wrap background task dispatching with centralized lifecycle state recording and local error capture to avoid unhandled task failures.

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
Claude Code MUST NOT skip or defer verification. All pull requests containing unawaited coroutines or blocking I/O calls within asynchronous contexts are blocked from merging.
</enforcement>