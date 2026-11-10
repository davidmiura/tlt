---
version: 2
name: cross-cutting-external-integration-adapters-communicat-22e0
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: External Integration Adapters Communicating Public Service"
metadata:
  actual:
    adr_id: 22e0a219-1bdd-428d-9118-c213595c57b6
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

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: External Integration Adapters Communicating Public Service

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/scripts/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all public HTTP endpoints accepting asynchronous external events, external adapters, boundary services, and internal event ingestion/classification nodes.

### Rules

- **R-CE-001** SHOULD: External integration adapters communicating with public service endpoints SHOULD deliver events over standard HTTP transport targeting designated event ingress routes.
- **R-CE-002** MANDATORY: Public ingress routers MUST operate as pass-through queues, forwarding valid envelopes directly into agent task queues without schema transformation.
- **R-CE-003** MANDATORY: Event classification functions MUST gracefully fall back to generic event triggers when receiving unknown event type identifiers while preserving all raw payload attributes.
- **R-CE-004** MANDATORY (DISCOVERY POLICY): The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-CE-005** MANDATORY (LOCK-VERSION GROUNDING): Before writing code that uses a versioned library, execute in order: (1) Find the dependency manifest in the repo declaring ranges, (2) Identify the build tool from the manifest, (3) Inspect the repository lock/resolution artifact to determine the exact resolved version, (4) Look up official documentation/changelog/API reference for that exact version without relying on training-data recall, (5) Confirm every API, class, or function called exists in that exact version's documentation, (6) Re-run steps 3-5 per dependency at point of use for version-sensitive behavior.

### Verify

```bash
# Discover the project test runner from repository configuration manifests and execute the test suite
# covering public event ingress routing and schema validation.
# Locate the linter and static type verification scripts from the project configuration and execute
# them across the shared event modules and routing packages.
```

**Accept when:**
- Public HTTP event ingress routes accept valid CloudEvent envelopes and successfully enqueue corresponding asynchronous processing tasks.
- Invalid event payloads lacking required envelope attributes are rejected at the ingress boundary with appropriate client error responses.
- Downstream event monitoring components successfully classify event type descriptors into internal trigger types without loss of context metadata.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests introducing non-standard public event endpoints or direct payload transformations at ingress are blocked at review, and runtime requests lacking mandatory envelope attributes must fail schema validation and return client error statuses.
</enforcement>