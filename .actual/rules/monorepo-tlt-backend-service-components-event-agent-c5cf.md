# Loguru Logging Adoption: Backend Service Components Event Agent Execution

These rules are ALWAYS ACTIVE for backend service endpoints, routers, asynchronous agent workflow nodes, task lifecycle tracking components, and protocol gateway implementations requiring operational diagnostics.

### Rules

- **R-LOG-001** MUST: Backend service components, event agent execution nodes, and protocol service modules MUST adopt the Loguru logging library by importing the unified logger object directly for all operational diagnostic logging.
- **R-LOG-002** MUST: Follow lock-version grounding before writing code using a versioned library: find the manifest, identify the build tool, inspect the repository lock or resolution artifact for the exact resolved version, check official docs for that version, and confirm every API/class/function exists in that version.
- **R-LOG-003** MUST: Import the preconfigured logger singleton directly from the logging library rather than reconfiguring handlers or formatters locally within functional units.
- **R-LOG-004** MUST: Ensure contextual variables such as task identifiers, event payload descriptors, and routing states are interpolated cleanly or passed as contextual parameters to facilitate traceability.

### Verify

```bash
# Discover and execute project static analysis and linting configuration scripts
# to verify logging library imports and invocations satisfy codebase standards.

# Identify and execute the test execution script declared in project configuration
# to confirm operational logging emits expected diagnostic records without runtime exceptions.
```

**Accept when:**
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>