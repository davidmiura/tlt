# Loguru Logging Adoption: Diagnostic Log Messages Emitted During Asynchronous

These rules are ALWAYS ACTIVE for backend service endpoints, routers managing event processing, task execution components, asynchronous agent workflow nodes, and task lifecycle tracking components.

### Rules

- **R-LOG-001** SHOULD: Diagnostic log messages emitted during asynchronous event processing include contextual metadata parameters such as event identifiers, task identifiers, and lifecycle state transitions.
- **R-LOG-002** MANDATORY: Import the preconfigured logger singleton directly from the logging library rather than reconfiguring handlers or formatters locally within functional units.
- **R-LOG-003** MANDATORY: Ensure contextual variables such as task identifiers, event payload descriptors, and routing states are interpolated cleanly or passed as contextual parameters to facilitate traceability.

### Verify

```bash
# Discover and execute project static analysis and linting scripts
# Discover and execute test execution scripts to verify logging telemetry emission
```

**Accept when:**
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration checks fail when prohibited logging patterns or unauthorized logging dependencies are introduced.
</enforcement>