# Loguru Logging Adoption: Before Writing Modifying Logging Code Consumer

These rules are ALWAYS ACTIVE for all backend service endpoints, routers, asynchronous agent workflow nodes, and protocol gateway implementations managing event processing and task execution.

### Rules

- **R-LOG-001** MUST: Before writing or modifying logging code, the consumer MUST inspect the repository dependency manifest and authoritative lock artifact to verify and resolve the exact locked version of the logging library.
- **R-LOG-002** MUST: Import the preconfigured logger singleton directly from the logging library rather than reconfiguring handlers or formatters locally within functional units.
- **R-LOG-003** MUST: Ensure contextual variables such as task identifiers, event payload descriptors, and routing states are interpolated cleanly or passed as contextual parameters to facilitate traceability.

### Verify

```bash
# Discover and execute project static analysis and linting configuration scripts from repository manifests
# Identify and execute the test execution script declared in project configuration
# Verify that prohibited standard library logger instantiations do not exist within service and agent directories
```

**Accept when:**
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration checks fail when prohibited logging patterns or unauthorized logging dependencies are introduced.
</enforcement>