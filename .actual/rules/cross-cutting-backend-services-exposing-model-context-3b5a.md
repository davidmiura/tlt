---
version: 2
name: cross-cutting-backend-services-exposing-model-context-3b5a
description: "FastMCP Framework Adoption for Model Context Protocol Services: Backend Services Exposing Model Context Protocol"
metadata:
  actual:
    adr_id: 3b5a0bd4-4d1a-4a60-b2ab-e2f64ac3044b
    status: accepted
    candidate_group_id: 462c56a1-fd0a-4b07-99e5-8e30b4c480b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# FastMCP Framework Adoption for Model Context Protocol Services: Backend Services Exposing Model Context Protocol

Scope: applies to `monorepo/tlt/mcp_services/**`.

These rules are ALWAYS ACTIVE for all backend services and modules responsible for exposing Model Context Protocol tools or context resources, and service runtime entrypoint definitions and protocol transport configuration modules.

### Rules

- **R-FMCP-001** MUST: Backend services exposing Model Context Protocol endpoints MUST adopt the FastMCP library as the standard framework for service instantiation, resource exposure, and tool registration.
- **R-FMCP-002** MANDATORY: The consumer MUST derive all tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-FMCP-003** MANDATORY: Before writing code that uses a versioned library, execute in order: (1) Find the dependency manifest; (2) Identify the build tool; (3) Inspect the repository lock or resolution artifact for the exact resolved version; (4) Look up official documentation/changelog for that exact version; (5) Confirm every API, class, or function exists in that version; (6) Re-run steps 3-5 per dependency at point of use for version-sensitive behavior.
- **R-FMCP-004** MUST: Isolate pure domain logic, state managers, and data calculation engines from FastMCP tool registration and resource routing decorators to ensure protocol boundaries remain distinct from core business rules.
- **R-FMCP-005** MUST: Maintain consistent hierarchical URI templates across service boundaries when exposing contextual data through FastMCP resource decorators.

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
Verified by automated continuous integration dependency and static analysis checks, as well as peer architecture and code reviews required for all service interface pull requests. Pull requests that define Model Context Protocol endpoints using unapproved server libraries or custom wire implementations will be blocked from merging.
</enforcement>