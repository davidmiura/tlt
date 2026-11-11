---
version: 2
name: cross-cutting-developers-inspect-repository-dependency-9172
description: "FastMCP Framework Adoption for Model Context Protocol Services: Developers Inspect Repository Dependency Manifest Authoritative"
metadata:
  actual:
    adr_id: 917273da-4cb2-4e9e-89f3-dbacbc0f3b08
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Developers Inspect Repository Dependency Manifest Authoritative

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources, and service runtime entrypoint definitions and protocol transport configuration modules.

### Rules

- **R-FASTMCP-001** MUST: Developers MUST inspect the repository dependency manifest and authoritative lock artifact to resolve the exact locked version of the FastMCP library before implementing or modifying protocol endpoints.

### Verify

```bash
# Discover and execute the project's dependency verification suite to confirm FastMCP usage and lock compliance
# Discover and run the repository's test suite to ensure all registered FastMCP tools and endpoints pass interface contracts
```

**Accept when:**
- All Model Context Protocol service runtimes instantiate their server definition using the FastMCP library class constructor.
- All exposed contextual protocol endpoints utilize the FastMCP resource URI decorator convention.
- Automated verification and integration test suites pass with zero protocol binding errors or unmapped tool endpoints.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>