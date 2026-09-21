# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Consumer Inspect Project Dependency Lock Artifact

These rules are ALWAYS ACTIVE for all external boundary adapters, client handlers, and HTTP ingress routes transmitting or receiving asynchronous events.

### Rules

- **R-CE-001** MUST: The consumer MUST inspect the project dependency lock artifact to verify the exact resolved version of the CloudEvents specification library prior to implementing or modifying event ingestion handlers.

### Verify

```bash
bash -c 'eval "$(discover_contract_test_command)"'
bash -c 'eval "$(discover_type_check_command)"'
bash -c 'eval "$(discover_linter_command)"'
```

**Accept when:**
- All boundary client event emissions conform to the CloudEvents specification and pass contract validation tests.
- Event ingestion endpoints accept CloudEvent payloads without mutation and enqueue them directly into the agent task queue.
- Event monitor nodes classify CloudEvent types into internal trigger types with accurate priority assignment and lifecycle tracking.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>