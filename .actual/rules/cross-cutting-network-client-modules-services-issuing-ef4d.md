---
version: 2
name: cross-cutting-network-client-modules-services-issuing-ef4d
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Network Client Modules Services Issuing Http"
metadata:
  actual:
    adr_id: ef4dc6b1-43c8-4988-856c-cf0b5aef0351
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

# Adoption of httpx for Asynchronous HTTP Client Communication: Network Client Modules Services Issuing Http

Scope: applies to `monorepo/tlt/adapters/discord_adapter/clients/**`, `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-NET-001** MUST: Network client modules and services issuing HTTP requests MUST use httpx.AsyncClient for all asynchronous HTTP interactions across service and adapter boundaries.

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