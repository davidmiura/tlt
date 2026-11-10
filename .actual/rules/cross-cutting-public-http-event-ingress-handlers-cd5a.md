---
version: 2
name: cross-cutting-public-http-event-ingress-handlers-cd5a
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Public Http Event Ingress Handlers Not"
metadata:
  actual:
    adr_id: cd5a9c97-a151-45e0-9f3c-a2dd1d6cb6f6
    status: accepted
    candidate_group_id: a6f6f686-17bf-4352-9cfd-e3550d75d771
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Public Http Event Ingress Handlers Not

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-CE-001** MUST_NOT: Public HTTP event ingress handlers MUST NOT mutate, transform, or deserialize domain payloads embedded within the event data attribute prior to asynchronous queue admission.

### Verify

```bash
# Discover the project test runner from repository configuration manifests and execute the test suite covering public event ingress routing and schema validation.
# Locate the linter and static type verification scripts from the project configuration and execute them across the shared event modules and routing packages.
```

**Accept when:**
- Public HTTP event ingress routes accept valid CloudEvent envelopes and successfully enqueue corresponding asynchronous processing tasks.
- Invalid event payloads lacking required envelope attributes are rejected at the ingress boundary with appropriate client error responses.
- Downstream event monitoring components successfully classify event type descriptors into internal trigger types without loss of context metadata.

<enforcement>
Claude Code MUST NOT skip or defer verification. Enforcement is verified by automated contract and schema validation test suites executed during continuous integration, static analysis rules verifying that public event ingress handlers consume the shared CloudEvent data model, and peer review of public API route additions and adapter integration changes.
</enforcement>