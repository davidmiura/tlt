---
version: 2
name: cross-cutting-instantiations-httpx-asyncclient-explici-1b99
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Instantiations Httpx Asyncclient Explicitly Configure Request"
metadata:
  actual:
    adr_id: 1b99a36b-a543-4338-925e-1d887c1478f8
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

# Adoption of httpx for Asynchronous HTTP Client Communication: Instantiations Httpx Asyncclient Explicitly Configure Request

Scope: applies to `monorepo/tlt/adapters/discord_adapter/clients/**`, `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HTTP-001** MUST: Instantiations of httpx.AsyncClient MUST explicitly configure a request timeout parameter rather than relying on default unbounded socket behavior.

### Verify

```bash
# Discover and run project static analysis and linting scripts to verify explicit timeout parameters on httpx.AsyncClient instantiations
# Discover and run the project automated test suite to validate asynchronous HTTP client communication
```

**Accept when:**
- Static analysis confirms all outbound HTTP client instantiations across services and adapters utilize httpx.AsyncClient with explicit timeout configurations.
- Automated test suites validate non-blocking asynchronous request execution and graceful handling of network timeouts.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>