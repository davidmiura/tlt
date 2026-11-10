---
version: 2
name: 42113271-4687-4124-be96-cabf7c2b4050-fastmcp-framework-adoption-for-model-context-protocol-services-domain-context-data-exposed-protocol-registered
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

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/mcp_services/**`

## Context

- The platform requires standardized mechanisms for exposing autonomous agent tools and contextual data resources across distributed microservices.
- Multiple independent domain services manage distinct capabilities such as event tracking, attendance responses, guild administration, and media validation.
- Without a unified server abstraction, services risk divergent implementations of Model Context Protocol transport handlers, tool signatures, and resource URI resolution.

## Problem Statement

Building Model Context Protocol microservices without a consistent library abstraction causes fragmented service entrypoints, bespoke JSON-RPC request handling, inconsistent resource URI schemas, and redundant tool registration logic across distributed domain components.

## Decision

1. MUST: Domain context data exposed to the protocol MUST be registered as addressable resource endpoints using the FastMCP resource URI decorator pattern.

## Policy Block

- MUST Domain context data exposed to the protocol MUST be registered as addressable resource endpoints using the FastMCP resource URI decorator pattern.

In scope:
- All backend services and modules responsible for exposing Model Context Protocol tools or context resources.
- Service runtime entrypoint definitions and protocol transport configuration modules.

Out of scope:
- Domain business engines and persistent data access layers operating internally without external Model Context Protocol interfaces.
- Stand-alone administrative or migration scripts that execute independently of protocol server runtimes.

## Rationale

- Fourteen modules across diverse functional domains consistently import and utilize FastMCP to manage server lifecycles, URI resource endpoints, and tool registration.
- FastMCP provides a clean, declarative interface for registering callable actions and contextual resources, ensuring structural consistency across the monorepo.
- Adopting FastMCP as the single standardized protocol framework avoids maintaining custom low-level protocol serialization and routing layers across each microservice.

## Consequences

Positive:
- Standardizes server lifecycle instantiation, tool registration, and resource URI routing across all Model Context Protocol service modules.
- Eliminates repetitive protocol protocol-handling boilerplate and reduces divergence in endpoint interface declarations.
- Accelerates development of new service capabilities through declarative decorators for tools and resource URIs.

Negative:
- Couples service entrypoints and protocol dispatch lifecycles to the conventions and release cadence of the FastMCP library.
- Requires developers to structure tool and resource endpoints according to the framework's decorator and registration patterns rather than generic callable functions.

## Alternatives

- Direct low-level implementation of the Model Context Protocol specification without an intermediary framework (rejected)
  Rejected because: Requires substantial redundant boilerplate for JSON-RPC transport framing, message serialization, and URI template routing across independent service boundaries
  When valid: When building minimal embedded agents under severe runtime memory constraints that preclude library dependencies
- Proprietary internal Model Context Protocol service orchestration layer (rejected)
  Rejected because: Incurs ongoing internal maintenance cost while duplicating standardized server primitives and decorator mechanisms available in the FastMCP library
  When valid: When proprietary transport protocols or non-standard message encodings must be supported across legacy infrastructure

## Risks

- Upstream protocol schema modifications or decorator signature changes in newer FastMCP releases could impact service compatibility.
  Mitigation: Enforce lock-version grounding by verifying resolved dependency artifacts and validating public documentation before upgrading the FastMCP library.
  Owner: Platform Engineering
- Coupling tool and resource registration to FastMCP abstractions could increase switching costs should an alternate protocol runtime be required.
  Mitigation: Maintain strict separation between domain state logic and FastMCP endpoint handler definitions to preserve business logic independence.
  Owner: Backend Engineering

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Isolate pure domain logic, state managers, and data calculation engines from FastMCP tool registration and resource routing decorators to ensure protocol boundaries remain distinct from core business rules.
- Maintain consistent hierarchical URI templates across service boundaries when exposing contextual data through FastMCP resource decorators.

## Continuation Context


Verify commands:
- Discover and execute the project's dependency verification suite to confirm that all Model Context Protocol service packages depend upon the locked version of the FastMCP library.
- Discover and run the repository's test suite to ensure all registered FastMCP tools, server instances, and resource URI endpoints satisfy protocol interface contracts.

Accept when:
- All Model Context Protocol service runtimes instantiate their server definition using the FastMCP library class constructor.
- All exposed contextual protocol endpoints utilize the FastMCP resource URI decorator convention.
- Automated verification and integration test suites pass with zero protocol binding errors or unmapped tool endpoints.

## Enforcement

- Verified by: Automated continuous integration dependency and static analysis checks.
- Verified by: Peer architecture and code reviews required for all service interface pull requests.
- Violation handling: Pull requests that define Model Context Protocol endpoints using unapproved server libraries or custom wire implementations will be blocked from merging.
- Violation handling: Non-compliant endpoint definitions must be refactored to use standard FastMCP server instantiations and registration handlers.
- Exception process: Submit an architectural review request to the platform architecture team detailing technical limitations preventing FastMCP usage along with an approved migration plan.