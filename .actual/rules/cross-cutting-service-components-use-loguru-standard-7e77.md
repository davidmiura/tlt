---
version: 2
name: cross-cutting-service-components-use-loguru-standard-7e77
description: "Loguru Logging Library: Service Components Use Loguru Standard Logging"
metadata:
  actual:
    adr_id: 7e77364f-dcfa-423b-81d5-af0be87ac199
    status: accepted
    candidate_group_id: 8a266a3f-c7bf-4e9e-8fc9-2346e2c48d8f
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# Loguru Logging Library: Service Components Use Loguru Standard Logging

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for service modules, background processing workflows, and tool handlers requiring operational or diagnostic telemetry.

### Rules

- **R-LOG-001** MUST: All service components MUST use Loguru as the standard logging framework for diagnostic, informational, and error logging.
- **R-LOG-002** MANDATORY: The consumer MUST discover the project's dependency manifest, build tool, and lock/resolution artifact to determine the exact resolved version of Loguru before writing code.
- **R-LOG-003** MANDATORY: Confirm every API, class, or function used from Loguru exists in that exact version's documentation before using it.
- **R-LOG-004** MANDATORY: Import logger from Loguru at the module top level and use contextual logging methods for error handling and event tracing.
- **R-LOG-005** MANDATORY: Configure global sinks and log levels during application initialization prior to executing background workflows.

### Verify

```bash
# Discover and execute the project's static analysis script to verify logging imports conform to the standard.
# Discover and execute the test runner script from the repository manifest to verify log emission behavior.
```

**Accept when:**
- All service modules import logger from loguru without introducing alternate logging frameworks or standard library logger boilerplate.
- Automated static analysis and test validation suites pass without logging-related lint or runtime errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated static analysis checks in CI pipelines and peer code reviews.
</enforcement>