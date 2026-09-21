# asyncio Asynchronous Concurrency Architecture: Coroutine Bodies Not Execute Blocking Synchronous

These rules are ALWAYS ACTIVE for all message adapter handlers, network endpoint routers, agent state execution workflow nodes, background event monitoring loops, scheduled timer evaluations, and asynchronous task dispatching pipelines.

### Rules

- **R-ASYNC-001** MUST_NOT: Coroutine bodies MUST_NOT execute blocking synchronous I/O operations or synchronous sleep functions that monopolize the active event loop thread.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>