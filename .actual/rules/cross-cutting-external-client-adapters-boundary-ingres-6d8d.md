---
version: 2
name: cross-cutting-external-client-adapters-boundary-ingres-6d8d
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: External Client Adapters Boundary Ingress Endpoints"
metadata:
  actual:
    adr_id: 6d8d4010-b321-4b17-954c-a80d2b3ae6b3
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

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: External Client Adapters Boundary Ingress Endpoints

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-EXT-001** MUST: All external client adapters and boundary ingress endpoints communicating with internal services MUST encapsulate event payloads within the shared CloudEvent data model provided by tlt.shared.cloudevents.

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
Claude Code MUST NOT skip or defer verification. Automated continuous integration contract tests, static type analysis, and schema compatibility linters enforce these rules; violations block pull requests.
</enforcement>