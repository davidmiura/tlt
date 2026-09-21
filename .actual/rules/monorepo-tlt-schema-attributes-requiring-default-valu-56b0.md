# Pydantic Adoption for Structured Domain and Event Validation: Schema Attributes Requiring Default Values Factory

These rules are ALWAYS ACTIVE for all domain models, agent context states, service task structures, and incoming/outgoing event payloads processed across asynchronous queues and service boundaries.

### Rules

- **R-PYD-001** MUST: Schema attributes requiring default values, factory functions, or boundary constraints MUST declare them using the Field specification interface.

### Verify

```bash
# Discover and run the project test suite runner for validation tests
# Discover and run the static analysis tool for type verification across model definitions
```

**Accept when:**
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated test suites and static type checking.
</enforcement>