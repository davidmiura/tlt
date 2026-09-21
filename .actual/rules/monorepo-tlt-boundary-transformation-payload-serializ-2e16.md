# Pydantic Adoption for Structured Domain and Event Validation: Boundary Transformation Payload Serialization Dictionary Representations

These rules are ALWAYS ACTIVE for all domain models representing business entities, agent context states, service task structures, and all incoming and outgoing event payloads processed across asynchronous queues and service boundaries.

### Rules

- **R-PYD-001** MUST: Boundary transformation and payload serialization to dictionary representations MUST be executed via the model_dump method rather than custom dictionary parsing or legacy serialization methods.

### Verify

```bash
# Discover and run the project test suite runner against all domain model and context definitions
# Discover and run the static analysis tool configuration to execute type verification across all data model declarations
```

**Accept when:**
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. All new domain entities and boundary payloads must inherit from BaseModel and use model_dump for serialization; untyped dictionary processing at service boundaries or models lacking validation will be blocked.
</enforcement>