# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Ingress Boundary Routes Not Discard Original

These rules are ALWAYS ACTIVE for all external boundary adapters, client handlers, and HTTP ingress routes receiving asynchronous events to internal agent orchestration services.

### Rules

- **R-CE-001** MUST_NOT: Ingress boundary routes MUST NOT discard original CloudEvent attributes or transform domain payloads prior to task queuing.

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