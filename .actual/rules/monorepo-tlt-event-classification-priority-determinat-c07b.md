# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Event Classification Priority Determination Domain Context

These rules are ALWAYS ACTIVE for all boundary adapters, HTTP ingress routers, and internal agent monitor nodes handling asynchronous client event ingestion and dispatch.

### Rules

- **R-ADR-001** MUST: Event classification, priority determination, and domain context extraction MUST be executed inside designated event monitor nodes rather than inside HTTP ingress routers.

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