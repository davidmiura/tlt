---
version: 2
name: cross-cutting-engineers-inspect-project-lock-artifact-7f42
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Engineers Inspect Project Lock Artifact Resolve"
metadata:
  actual:
    adr_id: 7f42d395-46fd-4500-a8f0-667426d41596
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

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Engineers Inspect Project Lock Artifact Resolve

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`, `monorepo/tlt/shared/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-CLI-001** MUST: Engineers MUST inspect the project lock artifact to resolve the exact dependency versions for internal event schema libraries prior to implementing or extending event handlers.

### Verify

```bash
# Discover and execute the project test runner for boundary integration tests
# Discover and run the project static type checker on boundary routing modules
# Discover and execute the contract verification task for schema compliance
```

**Accept when:**
- All ingress boundary endpoints accept and validate event payloads conforming to the shared event contract.
- Asynchronous task queues receive unmodified event instances with intact metadata attributes.
- All automated boundary verification and type checking suites pass without contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests introducing unencapsulated boundary payloads or mutated event structures are blocked by continuous integration.
</enforcement>