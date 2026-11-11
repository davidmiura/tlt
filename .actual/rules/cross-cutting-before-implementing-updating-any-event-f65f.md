---
version: 2
name: cross-cutting-before-implementing-updating-any-event-f65f
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Before Implementing Updating Any Event Serialization"
metadata:
  actual:
    adr_id: f65f48f9-ffe5-42a9-8cc6-9faf9dbbf63a
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

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Before Implementing Updating Any Event Serialization

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-CE-001** MUST: Before implementing or updating any event serialization or routing dependencies, developers MUST inspect the repository lock artifact to determine the exact resolved dependency version and verify that all invoked interfaces match that resolved specification.

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
Claude Code MUST NOT skip or defer verification. Automated contract and schema validation test suites executed during continuous integration, static analysis rules, and peer review enforce these requirements.
</enforcement>