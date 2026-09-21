# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Event Monitor Nodes Preserve Cloudevent Metadata

These rules are ALWAYS ACTIVE for all external boundary adapters, client handlers, and event monitor nodes processing asynchronous event ingestion.

### Rules

- **R-CE-001** MUST: Event monitor nodes MUST preserve CloudEvent metadata, including identifier, source, type, and timestamp, within structured context containers across the entire task lifecycle.

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