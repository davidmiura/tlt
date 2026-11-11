---
version: 2
name: cross-cutting-downstream-event-processing-nodes-valida-25c3
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Downstream Event Processing Nodes Validate Classify"
metadata:
  actual:
    adr_id: 25c39ef0-5eaa-45a9-8d56-e94fbc699a7a
    status: accepted
    candidate_group_id: 4bdbe324-bdbd-46cc-b3c9-4ba5cff2bd7c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Downstream Event Processing Nodes Validate Classify

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all external client adapters communicating asynchronously with internal services, all boundary ingress endpoints accepting external event notifications or triggers, and all background task dispatchers handling external client events.

### Rules

- **R-CE-001** MUST: Downstream event processing nodes MUST validate and classify incoming CloudEvent metadata attributes including type, source, subject, and timestamp before executing domain logic.

### Verify

```bash
# Discover the project test runner configured in the dependency manifest and execute the boundary integration test suite.
# Discover the project static type checker and run type verification on all boundary routing modules.
# Discover the contract verification task in the project configuration and execute schema compliance checks.
```

**Accept when:**
- All ingress boundary endpoints accept and validate event payloads conforming to the shared event contract.
- Asynchronous task queues receive unmodified event instances with intact metadata attributes.
- All automated boundary verification and type checking suites pass without contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>