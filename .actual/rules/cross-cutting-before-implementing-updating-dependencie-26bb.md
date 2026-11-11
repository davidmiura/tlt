---
version: 2
name: cross-cutting-before-implementing-updating-dependencie-26bb
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Before Implementing Updating Dependencies Involving Httpx"
metadata:
  actual:
    adr_id: 26bb83e5-279c-404d-9475-dd4e77c5f8a7
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

# Adoption of httpx for Asynchronous HTTP Client Communication: Before Implementing Updating Dependencies Involving Httpx

Scope: applies to `monorepo/tlt/adapters/discord_adapter/clients/**`, `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-HTTPX-001** MUST: Before implementing or updating dependencies involving httpx, the consumer MUST discover the project dependency lock artifact and verify the exact resolved version against official documentation.

### Verify

```bash
# Discover and run project dependency checks, static analysis, linting, and automated tests
find_lock_file=$(find . -maxdepth 3 \( -name "poetry.lock" -o -name "uv.lock" -o -name "Pipfile.lock" -o -name "Cargo.lock" -o -name "package-lock.json" -o -name "pnpm-lock.yaml" -o -name "yarn.lock" }))
echo "Found lock file: $find_lock_file"

# Run linting/static analysis if available in project
if command -v pytest &> /dev/null; then
  pytest
fi
```

**Accept when:**
- Static analysis confirms all outbound HTTP client instantiations across services and adapters utilize httpx.AsyncClient with explicit timeout configurations.
- Automated test suites validate non-blocking asynchronous request execution and graceful handling of network timeouts.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>