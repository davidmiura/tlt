---
version: 2
name: cross-cutting-ingress-boundary-routers-ingest-incoming-35fb
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Ingress Boundary Routers Ingest Incoming Cloudevent"
metadata:
  actual:
    adr_id: 35fbef71-6919-42ad-80b2-361f66e023a3
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

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Ingress Boundary Routers Ingest Incoming Cloudevent

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-CIB-001** MUST: Ingress boundary routers MUST ingest incoming CloudEvent instances without mutating or transforming the payload data prior to asynchronous queue dispatch.

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
Claude Code MUST NOT skip or defer verification. All pull requests introducing unencapsulated boundary payloads or mutated event structures are blocked by continuous integration.
</enforcement>