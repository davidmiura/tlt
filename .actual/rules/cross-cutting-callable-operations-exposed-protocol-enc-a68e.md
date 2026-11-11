---
version: 2
name: cross-cutting-callable-operations-exposed-protocol-enc-a68e
description: "FastMCP Framework Adoption for Model Context Protocol Services: Callable Operations Exposed Protocol Encapsulated Within"
metadata:
  actual:
    adr_id: a68e05c3-3f15-4e38-b908-a27161ec6bb9
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Callable Operations Exposed Protocol Encapsulated Within

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources, and service runtime entrypoint definitions and protocol transport configuration modules.

### Rules

- **R-MCP-001** MUST: Callable operations exposed to the protocol MUST be encapsulated within dedicated tool registration handlers associated with the service instance.
- **R-MCP-002** MANDATORY: Discover the dependency manifest in the repo to find the locked FastMCP version before writing version-dependent code.
- **R-MCP-003** MUST: Isolate pure domain logic, state managers, and data calculation engines from FastMCP tool registration and resource routing decorators to ensure protocol boundaries remain distinct from core business rules.
- **R-MCP-004** MUST: Maintain consistent hierarchical URI templates across service boundaries when exposing contextual data through FastMCP resource decorators.

### Verify

```bash
# Discover and execute the project's dependency verification suite to confirm FastMCP usage and lock version adherence
# (Repository-specific discovery required)
```

**Accept when:**
- All Model Context Protocol service runtimes instantiate their server definition using the FastMCP library class constructor.
- All exposed contextual protocol endpoints utilize the FastMCP resource URI decorator convention.
- Automated verification and integration test suites pass with zero protocol binding errors or unmapped tool endpoints.

<enforcement>
Claude Code MUST NOT skip or defer verification. All Model Context Protocol endpoints must use standard FastMCP server instantiations and registration handlers, verified via automated CI static analysis and peer code reviews.
</enforcement>