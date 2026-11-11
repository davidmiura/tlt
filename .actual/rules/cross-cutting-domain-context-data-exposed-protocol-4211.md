---
version: 2
name: cross-cutting-domain-context-data-exposed-protocol-4211
description: "FastMCP Framework Adoption for Model Context Protocol Services: Domain Context Data Exposed Protocol Registered"
metadata:
  actual:
    adr_id: 42113271-4687-4124-be96-cabf7c2b4050
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Domain Context Data Exposed Protocol Registered

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources, and service runtime entrypoint definitions and protocol transport configuration modules.

### Rules

- **R-MCP-001** MUST: Domain context data exposed to the protocol MUST be registered as addressable resource endpoints using the FastMCP resource URI decorator pattern.
- **R-MCP-002** MANDATORY: Execute lock-version grounding before writing code that uses a versioned library: find the dependency manifest, identify the build tool, inspect the repository lock or resolution artifact to determine the exact resolved version, look up official documentation/changelog for that exact version, confirm every API/class/function exists in that version's documentation, and re-verify per dependency at point of use for version-sensitive behavior.
- **R-MCP-003** MANDATORY: Isolate pure domain logic, state managers, and data calculation engines from FastMCP tool registration and resource routing decorators to ensure protocol boundaries remain distinct from core business rules.
- **R-MCP-004** MANDATORY: Maintain consistent hierarchical URI templates across service boundaries when exposing contextual data through FastMCP resource decorators.

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
Claude Code MUST NOT skip or defer verification. Pull requests that define Model Context Protocol endpoints using unapproved server libraries or custom wire implementations will be blocked from merging.
</enforcement>