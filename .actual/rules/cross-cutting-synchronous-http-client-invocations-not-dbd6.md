---
version: 2
name: cross-cutting-synchronous-http-client-invocations-not-dbd6
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Synchronous Http Client Invocations Not Executed"
metadata:
  actual:
    adr_id: dbd67dd8-e55a-4212-baca-bbe817337293
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

# Adoption of httpx for Asynchronous HTTP Client Communication: Synchronous Http Client Invocations Not Executed

Scope: applies to `monorepo/tlt/adapters/discord_adapter/clients/**`, `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all asynchronous services, microservices, and protocol adapters initiating outbound HTTP requests.

### Rules

- **R-HTTP-001** MUST_NOT: Synchronous HTTP client invocations MUST NOT be executed within asynchronous service or adapter workflows.

### Verify

```bash
# Discover and run the project static analysis and linting scripts to verify that HTTP client instantiations use httpx.AsyncClient with explicit timeout parameters.
# Discover and run the project automated test suite to validate asynchronous HTTP client communication across service and adapter boundaries.
```

**Accept when:**
- Static analysis confirms all outbound HTTP client instantiations across services and adapters utilize httpx.AsyncClient with explicit timeout configurations.
- Automated test suites validate non-blocking asynchronous request execution and graceful handling of network timeouts.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>