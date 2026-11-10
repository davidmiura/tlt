---
version: 2
name: cross-cutting-services-not-introduce-alternative-model-669f
description: "FastMCP Framework Adoption for Model Context Protocol Services: Services Not Introduce Alternative Model Context"
metadata:
  actual:
    adr_id: 669f5af4-caa2-44b7-a44d-3193c5d14c26
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Services Not Introduce Alternative Model Context

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources.

### Rules

- **R-MCP-001** MUST_NOT: Services MUST NOT introduce alternative Model Context Protocol server frameworks or bypass FastMCP protocol dispatch mechanisms within protocol service modules.

### Verify

```bash
# Discover and execute the project's dependency verification suite to confirm that all Model Context Protocol service packages depend upon the locked version of the FastMCP library.
# Discover and run the repository's test suite to ensure all registered FastMCP tools, server instances, and resource URI endpoints satisfy protocol interface contracts.
```

**Accept when:**
- All Model Context Protocol service runtimes instantiate their server definition using the FastMCP library class constructor.
- All exposed contextual protocol endpoints utilize the FastMCP resource URI decorator convention.
- Automated verification and integration test suites pass with zero protocol binding errors or unmapped tool endpoints.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>