# Adoption of uvicorn as Core ASGI Server Runtime: Components Running Long Lived Background Protocols

These rules are ALWAYS ACTIVE for backend services and adapters exposing network contracts or HTTP endpoints, and service entrypoints responsible for process lifecycle orchestration and ASGI interface hosting.

### Rules

- **R-UVC-001** SHOULD: Components running long-lived background protocols alongside the HTTP server SHOULD isolate background loops to prevent event loop contention.

### Verify

```bash
# Discover and run the project test runner script defined in the project configuration.
# Discover and execute the dependency audit script to verify declared server runtime dependencies against the lock artifact.
# Discover and run the static linter script across entrypoint modules to verify lifecycle compliance.
```

**Accept when:**
- The service entrypoint executes successfully and serves HTTP API routes via the configured ASGI server runtime.
- Static dependency and import analysis confirms that server lifecycle bindings conform to ASGI application contracts without direct process coupling violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>