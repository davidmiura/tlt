---
version: 2
name: cross-cutting-boundary-routers-serialize-cloudevent-st-a694
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Boundary Routers Serialize Cloudevent Structure Internal"
metadata:
  actual:
    adr_id: a6946c19-5400-4b47-ba49-120e37be79da
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

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Boundary Routers Serialize Cloudevent Structure Internal

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all external client adapters communicating asynchronously with internal services, boundary ingress endpoints accepting external event notifications or triggers, and background task dispatchers handling external client events.

### Rules

- **R-BOUNDARY-001** MUST: Boundary routers MUST serialize the CloudEvent structure into internal task representations using model_dump to preserve original event attributes across process boundaries.

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
Claude Code MUST NOT skip or defer verification. Compliance is verified by automated continuous integration contract tests, static type analysis, schema compatibility linters, and peer code reviews.
</enforcement>