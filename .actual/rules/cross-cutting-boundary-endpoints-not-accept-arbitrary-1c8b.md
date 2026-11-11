---
version: 2
name: cross-cutting-boundary-endpoints-not-accept-arbitrary-1c8b
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Boundary Endpoints Not Accept Arbitrary Untyped"
metadata:
  actual:
    adr_id: 1c8ba913-f963-4464-b94f-12ce25ead2ad
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

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Boundary Endpoints Not Accept Arbitrary Untyped

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all external client adapters, boundary ingress endpoints accepting external event notifications, and background task dispatchers handling external client events.

### Rules

- **R-BOUND-001** MUST_NOT: Boundary endpoints MUST NOT accept arbitrary untyped payloads for asynchronous event triggers without conforming to the CloudEvent specification envelope.

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
Claude Code MUST NOT skip or defer verification. All new external adapter and ingress router implementations are verified by automated continuous integration contract tests, static type analysis, schema compatibility linters, and peer code review. Pull requests introducing unencapsulated boundary payloads or mutated event structures are blocked by CI.
</enforcement>