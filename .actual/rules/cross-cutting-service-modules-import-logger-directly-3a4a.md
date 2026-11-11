---
version: 2
name: cross-cutting-service-modules-import-logger-directly-3a4a
description: "Loguru Logging Library: Service Modules Import Logger Directly Loguru"
metadata:
  actual:
    adr_id: 3a4a0b1b-c6c8-4f40-9215-2e0d18db0468
    status: accepted
    candidate_group_id: 8a266a3f-c7bf-4e9e-8fc9-2346e2c48d8f
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# Loguru Logging Library: Service Modules Import Logger Directly Loguru

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for service modules, background processing workflows, and tool handlers requiring operational or diagnostic telemetry.

### Rules

- **R-LOG-001** MUST: Service modules MUST import logger directly from loguru and invoke its standard logging methods rather than instantiating independent logging clients.

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