---
version: 2
name: cross-cutting-before-implementing-code-that-depends-f3c4
description: "Loguru Logging Library: Before Implementing Code That Depends Loguru"
metadata:
  actual:
    adr_id: f3c42301-4e91-40eb-8eb4-3bab050466ab
    status: accepted
    candidate_group_id: 8a266a3f-c7bf-4e9e-8fc9-2346e2c48d8f
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# Loguru Logging Library: Before Implementing Code That Depends Loguru

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for service modules, background processing workflows, and tool handlers requiring operational or diagnostic telemetry.

### Rules

- **R-LOG-001** MUST: Before implementing code that depends on Loguru, consumers MUST inspect the project lock artifact to resolve the exact dependency version and adhere strictly to its documented API contracts.

### Verify

```bash
# Discover the project's static analysis script in the workspace configuration and execute it to verify logging imports conform to the standard.
# Discover the project's test runner script from the repository manifest and execute the test suite to verify log emission behavior.
```

**Accept when:**
- All service modules import logger from loguru without introducing alternate logging frameworks or standard library logger boilerplate.
- Automated static analysis and test validation suites pass without logging-related lint or runtime errors.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>