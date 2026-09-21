# Adoption of uvicorn as Core ASGI Server Runtime: Entrypoint Implementations Not Embed Hardcoded Server

These rules are ALWAYS ACTIVE for backend services and adapters exposing network contracts or HTTP endpoints, and service entrypoints responsible for process lifecycle orchestration and ASGI interface hosting.

### Rules

- **R-ENT-001** MUST_NOT: Entrypoint implementations MUST NOT embed hardcoded server network addresses, ports, or credentials in source code and MUST resolve runtime configuration through environment sources.

### Verify

```bash
# Discover and run the project test runner script defined in the project configuration
# Discover and execute the dependency audit script to verify declared server runtime dependencies against the lock artifact
# Discover and run the static linter script across entrypoint modules to verify lifecycle compliance
```

**Accept when:**
- The service entrypoint executes successfully and serves HTTP API routes via the configured ASGI server runtime.
- Static dependency and import analysis confirms that server lifecycle bindings conform to ASGI application contracts without direct process coupling violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by continuous integration build pipelines, automated static analysis, and code review gates inspecting entrypoint server initialization.
</enforcement>