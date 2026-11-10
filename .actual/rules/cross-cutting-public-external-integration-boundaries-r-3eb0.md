---
version: 2
name: cross-cutting-public-external-integration-boundaries-r-3eb0
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Public External Integration Boundaries Receiving Asynchronous"
metadata:
  actual:
    adr_id: 3eb0ee75-ae77-4bf2-9c48-04e7b7760ef8
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

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Public External Integration Boundaries Receiving Asynchronous

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public HTTP endpoints accepting asynchronous external events, external adapters, boundary services, and internal event ingestion/classification nodes.

### Rules

- **R-CE-001** MUST: Public external integration boundaries receiving asynchronous incoming events MUST ingest all payloads wrapped in the CloudEvent envelope data structure defined by the shared CloudEvents module.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>