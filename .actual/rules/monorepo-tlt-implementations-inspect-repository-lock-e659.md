# Adoption of uvicorn as Core ASGI Server Runtime: Implementations Inspect Repository Lock Artifact Verify

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ADR-001** MUST: Implementations MUST inspect the repository lock artifact and verify the exact resolved version of the server runtime dependency prior to invoking server runtime interfaces.

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
Claude Code MUST NOT skip or defer verification. Continuous integration build pipelines verify dependencies against the project lock artifact.
</enforcement>