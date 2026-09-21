# Pydantic Adoption for Structured Domain and Event Validation: Service Boundary Ingestion Endpoints Not Process

These rules are ALWAYS ACTIVE for all domain models representing business entities, agent context states, service task structures, and incoming or outgoing event payloads processed across asynchronous queues and service boundaries.

### Rules

- **R-PYD-001** MUST_NOT: Service boundary ingestion endpoints MUST_NOT process unvalidated dictionary payloads directly into core workflows without first deserializing and validating them through an appropriate BaseModel definition.

### Verify

```bash
# Discover and run test suite runner from repository manifests to validate domain models and contexts
# Discover and run static analysis tool configuration from repository manifests to verify types
```

**Accept when:**
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests containing untyped dictionary processing at service boundaries or models lacking validation are blocked from merging.
</enforcement>