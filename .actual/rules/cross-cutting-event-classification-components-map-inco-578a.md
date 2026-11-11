---
version: 2
name: cross-cutting-event-classification-components-map-inco-578a
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Event Classification Components Map Incoming Type"
metadata:
  actual:
    adr_id: 578a537b-2432-4010-9e2c-ddb2fee9f0f1
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

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Event Classification Components Map Incoming Type

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public HTTP endpoints accepting asynchronous external events, adapter notifications, external adapters and boundary services publishing events, and internal event ingestion and classification nodes.

### Rules

- **R-CE-001** MUST: Event classification components MUST map incoming event type descriptors to internal event trigger types and extract contextual metadata into structured event contexts.

### Verify

```bash
# Discover and execute project test runner for public event ingress routing and schema validation
# Locate and execute linter and static type verification scripts across shared event modules and routing packages
```

**Accept when:**
- Public HTTP event ingress routes accept valid CloudEvent envelopes and successfully enqueue corresponding asynchronous processing tasks.
- Invalid event payloads lacking required envelope attributes are rejected at the ingress boundary with appropriate client error responses.
- Downstream event monitoring components successfully classify event type descriptors into internal trigger types without loss of context metadata.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated contract and schema validation test suites, static analysis rules, and peer review.
</enforcement>