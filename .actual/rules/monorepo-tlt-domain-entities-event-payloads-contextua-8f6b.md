# Pydantic Adoption for Structured Domain and Event Validation: Domain Entities Event Payloads Contextual State

These rules are ALWAYS ACTIVE for all domain models representing business entities, agent context states, service task structures, and all incoming/outgoing event payloads processed across asynchronous queues and service boundaries.

### Rules

- **R-PYD-001** MUST: All domain entities, event payloads, and contextual state structures MUST be defined as Pydantic models inheriting from BaseModel.

### Verify

```bash
# Discover the project test suite runner from repository manifests and execute validation tests against all domain model and context definitions.
# Discover the static analysis tool configuration from repository manifests and execute type verification across all data model declarations.
```

**Accept when:**
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. All new domain entities and boundary payloads must inherit from BaseModel, and type checking and tests must pass.
</enforcement>