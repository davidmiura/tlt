# Loguru Logging Adoption: New Backend Services Event Agent Nodes

These rules are ALWAYS ACTIVE for all backend service endpoints, routers managing event processing and task execution, asynchronous agent workflow nodes, task lifecycle tracking components, protocol gateway implementations, and modular service tools requiring operational diagnostics.

### Rules

- **R-LOG-001** MUST_NOT: New backend services, event agent nodes, or protocol tools MUST NOT introduce per-module standard library logger instantiation boilerplate.

### Verify

```bash
# Discover and execute project static analysis / linting configuration scripts to verify logging imports and invocations
# Discover and execute test execution script to confirm operational logging emits expected diagnostic records
# Execute codebase verification scripts to ensure prohibited standard library logger instantiations do not exist
```

**Accept when:**
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>