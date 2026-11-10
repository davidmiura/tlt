---
version: 2
name: cross-cutting-each-model-context-protocol-service-bf4e
description: "FastMCP Framework Adoption for Model Context Protocol Services: Each Model Context Protocol Service Entrypoint"
metadata:
  actual:
    adr_id: bf4e4010-1492-4147-8f15-022808ca4373
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Each Model Context Protocol Service Entrypoint

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources, and service runtime entrypoint definitions and protocol transport configuration modules.

### Rules

- **R-MCP-001** MUST: Each Model Context Protocol service entrypoint MUST instantiate its server definition using the FastMCP class constructor with an explicit service identifier.
- **R-MCP-002** MUST: Isolate pure domain logic, state managers, and data calculation engines from FastMCP tool registration and resource routing decorators to ensure protocol boundaries remain distinct from core business rules.
- **R-MCP-003** MUST: Maintain consistent hierarchical URI templates across service boundaries when exposing contextual data through FastMCP resource decorators.
- **R-MCP-004** MUST: Execute lock-version grounding (finding manifest, identifying build tool, inspecting lock/resolution artifact, looking up official docs for that exact version, confirming API existence) before writing code that uses a versioned library.

### Verify

```bash
# Discover and execute the project's dependency verification suite to confirm that all Model Context Protocol service packages depend upon the locked version of the FastMCP library.
# Discover and run the repository's test suite to ensure all registered FastMCP tools, server instances, and resource URI endpoints satisfy protocol interface contracts.
# (Exact discovery commands depend on the project repository's build system and test runner)
```

**Accept when:**
- All Model Context Protocol service runtimes instantiate their server definition using the FastMCP library class constructor.
- All exposed contextual protocol endpoints utilize the FastMCP resource URI decorator convention.
- Automated verification and integration test suites pass with zero protocol binding errors or unmapped tool endpoints.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests defining Model Context Protocol endpoints using unapproved server libraries or custom wire implementations will be blocked from merging.
</enforcement>