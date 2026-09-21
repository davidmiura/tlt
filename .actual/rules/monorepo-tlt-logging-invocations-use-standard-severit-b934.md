# Loguru Logging Adoption: Logging Invocations Use Standard Severity Methods

These rules are ALWAYS ACTIVE for backend service endpoints, routers, asynchronous agent workflow nodes, task lifecycle tracking components, and protocol gateway implementations.

### Rules

- **R-LOG-001** MUST: Logging invocations MUST use the standard severity methods provided by the logger singleton corresponding to the operational significance of the event.

### Verify

```bash
# Discover and execute project static analysis and linting configuration scripts
# Discover and execute test execution scripts declared in the project configuration
```

**Accept when:**
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration checks fail when prohibited logging patterns or unauthorized logging dependencies are introduced.
</enforcement>