# Adoption of uvicorn as Core ASGI Server Runtime: Services Adapters Exposing Asynchronous Http Contracts

These rules are ALWAYS ACTIVE for backend services and adapters exposing network contracts or HTTP endpoints, and service entrypoints responsible for process lifecycle orchestration and ASGI interface hosting.

### Rules

- **R-UVICORN-001** MUST: Services and adapters exposing asynchronous HTTP API contracts MUST adopt uvicorn as their core ASGI server runtime.
- **R-UVICORN-002** MANDATORY: The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-UVICORN-003** MANDATORY: Before writing code that uses a versioned library, execute the lock-version grounding process in order (find dependency manifest, identify build tool, inspect repository lock/resolution artifact, look up official documentation for that exact version, confirm every API exists, re-run per dependency at point of use).
- **R-UVICORN-004** MUST: Configure server instances through externalized environment sources rather than hardcoded configuration properties.
- **R-UVICORN-005** MUST: Structure application lifespan contracts to manage clean resource initialization and shutdown alongside server execution.
- **R-UVICORN-006** MUST: Isolate blocking background operations onto dedicated worker threads or external worker queues to prevent starvation of the event loop.
- **R-UVICORN-007** MUST: Enforce strict lock-file version resolution and execute integration smoke tests on dependency updates to prevent behavioral drift.

### Verify

\`\`\`bash
# Discover and run the project test runner script defined in the project configuration.
# Discover and execute the dependency audit script to verify declared server runtime dependencies against the lock artifact.
# Discover and run the static linter script across entrypoint modules to verify lifecycle compliance.
\`\`\`

**Accept when:**
- The service entrypoint executes successfully and serves HTTP API routes via the configured ASGI server runtime.
- Static dependency and import analysis confirms that server lifecycle bindings conform to ASGI application contracts without direct process coupling violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration build pipelines and automated static analysis verify dependencies against the project lock artifact and inspect entrypoint server initialization.
</enforcement>