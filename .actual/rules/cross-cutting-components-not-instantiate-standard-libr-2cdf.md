---
version: 2
name: cross-cutting-components-not-instantiate-standard-libr-2cdf
description: "Loguru Logging Library: Components Not Instantiate Standard Library Logging"
metadata:
  actual:
    adr_id: 2cdf2f5d-5723-4492-bd55-54386ea285ab
    status: accepted
    candidate_group_id: 8a266a3f-c7bf-4e9e-8fc9-2346e2c48d8f
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# Loguru Logging Library: Components Not Instantiate Standard Library Logging

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for service modules, background processing workflows, and tool handlers requiring operational or diagnostic telemetry.

### Rules

- **R-LOG-001** MUST_NOT: Components MUST NOT instantiate standard library logging handlers or implement parallel logging abstractions that bypass the adopted logging library.

### Verify

```bash
# Discover and execute the project's static analysis script
# Discover and execute the test runner script from the repository manifest
```

**Accept when:**
- All service modules import logger from loguru without introducing alternate logging frameworks or standard library logger boilerplate.
- Automated static analysis and test validation suites pass without logging-related lint or runtime errors.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>