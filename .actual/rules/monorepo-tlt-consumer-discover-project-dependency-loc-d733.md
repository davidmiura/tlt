# Pydantic Adoption for Structured Domain and Event Validation: Consumer Discover Project Dependency Lock Artifact

These rules are ALWAYS ACTIVE for all domain models representing business entities, agent context states, and service task structures, and all incoming and outgoing event payloads processed across asynchronous queues and service boundaries.

### Rules

- **R-PYD-001** MUST: The consumer MUST discover the project dependency lock artifact and verify the exact resolved version of the data validation library before invoking schema definition or serialization interfaces.

### Verify

```bash
# Discover and run the project test suite runner
# Discover and execute the static analysis tool configuration
```

**Accept when:**
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated test suites, static type checking, and peer code review enforce model validation, type annotations, and BaseModel inheritance. Violations block pull requests from merging.
</enforcement>