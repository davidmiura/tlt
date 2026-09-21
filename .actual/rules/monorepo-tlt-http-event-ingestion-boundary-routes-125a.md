# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Http Event Ingestion Boundary Routes Accept

These rules are ALWAYS ACTIVE for all external boundary adapters, client handlers, and HTTP ingress routes receiving asynchronous events destined for internal agent orchestration services.

### Rules

- **R-CEI-001** MUST: HTTP event ingestion boundary routes MUST accept CloudEvent instances directly and forward the payload into the agent task queue without performing transport-level data mutation.

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
Claude Code MUST NOT skip or defer verification. All pull requests introducing non-CloudEvent payload contracts or performing in-flight mutation on raw event payloads will be rejected.
</enforcement>