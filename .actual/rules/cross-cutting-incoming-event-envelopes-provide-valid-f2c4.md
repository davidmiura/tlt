---
version: 2
name: cross-cutting-incoming-event-envelopes-provide-valid-f2c4
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Incoming Event Envelopes Provide Valid Identifier"
metadata:
  actual:
    adr_id: f2c485c1-a8c8-4d03-9a24-2ea253ecad4f
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

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Incoming Event Envelopes Provide Valid Identifier

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public HTTP endpoints accepting asynchronous external events, adapter notifications, external adapters, boundary services, and internal event ingestion/classification nodes.

### Rules

- **R-CE-001** MUST: All incoming event envelopes MUST provide valid event identifier, source identifier, event type descriptor, and specification version attributes.

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
Claude Code MUST NOT skip or defer verification. All pull requests introducing non-standard public event endpoints or direct payload transformations at ingress must be blocked.
</enforcement>