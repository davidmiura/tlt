---
version: 2
name: cross-cutting-http-client-instances-maintained-shared-f3ad
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Http Client Instances Maintained Shared Long"
metadata:
  actual:
    adr_id: f3ad8b49-eeca-480b-8503-7cd9daff2138
    status: accepted
    candidate_group_id: 4ba16875-5686-4b4a-88d5-dd99eac3ca39
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/clients/**
      - tlt/mcp_services/**
---

# Adoption of httpx for Asynchronous HTTP Client Communication: Http Client Instances Maintained Shared Long

Scope: applies to `monorepo/tlt/adapters/discord_adapter/clients/**`, `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for asynchronous services, microservices, and protocol adapters initiating outbound HTTP requests.

### Rules

- **R-HTTP-001** SHOULD: HTTP client instances SHOULD be maintained as shared long-lived dependencies or bound to component lifecycles to optimize connection pooling.

### Verify

```bash
# Discover and run the project static analysis and linting scripts to verify that HTTP client instantiations use httpx.AsyncClient with explicit timeout parameters.
# Discover and run the project automated test suite to validate asynchronous HTTP client communication across service and adapter boundaries.
```

**Accept when:**
- Static analysis confirms all outbound HTTP client instantiations across services and adapters utilize httpx.AsyncClient with explicit timeout configurations.
- Automated test suites validate non-blocking asynchronous request execution and graceful handling of network timeouts.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated static analysis, linting, and peer code review.
</enforcement>