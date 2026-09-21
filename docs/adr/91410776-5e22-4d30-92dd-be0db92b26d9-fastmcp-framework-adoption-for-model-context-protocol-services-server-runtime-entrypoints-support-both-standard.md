# FastMCP Framework Adoption for Model Context Protocol Services: Server Runtime Entrypoints Support Both Standard

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Services interfacing with external agentic clients require a standardized protocol interface to expose callable tools and queryable resources.
- Adopting FastMCP establishes a consistent server abstraction across protocol endpoints while delegating domain logic to service components.
- Code evidence across multiple modules demonstrates structured FastMCP server initialization, tool registration, and resource URI endpoints.

## Problem Statement

Exposing service capabilities to external agentic clients without a consistent protocol framework risks fragmented serialization, fragmented transport handling, and tight coupling between protocol mechanics and core domain services.

## Decision

1. SHOULD: Server runtime entrypoints SHOULD support both standard input-output and network transport modes selected via environment configuration.

## Policy Block

- SHOULD Server runtime entrypoints SHOULD support both standard input-output and network transport modes selected via environment configuration.

In scope:
- All service components exposing Model Context Protocol tools, resources, or server transports to external clients and agents.

Out of scope:
- Internal domain services, persistence layers, and utility modules that do not interface directly with external Model Context Protocol clients.

## Rationale

- FastMCP provides a lightweight, declarative framework for building Model Context Protocol servers with standardized tool and resource primitives.
- Separating protocol endpoints into dedicated tool and resource registration modules preserves modularity and keeps domain services independent of transport protocols.
- Support for both standard input-output and network transport modes enables flexible deployment across diverse client integration contexts.

## Consequences

Positive:
- Standardizes external client and agent access through unified Model Context Protocol tool and resource contracts.
- Decouples transport hosting configuration from internal business logic and state management services.
- Simplifies registration of declarative resource URIs and callable agent tools.

Negative:
- Introduces runtime dependency on the FastMCP framework and its underlying protocol protocol serialization assumptions.
- Requires synchronization between FastMCP tool signature definitions and internal service method signatures.

## Alternatives

- Direct low-level JSON-RPC protocol implementation over raw standard input-output and network sockets (rejected)
  Rejected because: Requires maintaining custom protocol framing, serialization schemas, and transport abstractions rather than leveraging standardized protocol bindings.
  When valid: Valid only when runtime constraints preclude external library dependencies or custom binary protocols are mandated.
- Monolithic service module combining transport initialization, protocol schemas, and data persistence in a single file (rejected)
  Rejected because: Tightly couples transport protocol lifecycle with domain business logic, hindering modular testing and extensibility.
  When valid: Valid only for ephemeral prototypes or single-function proof-of-concept scripts.

## Risks

- Upstream API changes in FastMCP could affect server startup or protocol registration mechanics.
  Mitigation: Pin dependencies strictly via repository lock artifacts and isolate protocol decorators behind interface registration layers.
  Owner: engineering team
- Misconfiguration between standard input-output and network transport modes could lead to service unresponsiveness in production environments.
  Mitigation: Implement comprehensive integration tests covering both transport modes and enforce configuration defaults.
  Owner: engineering team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Structure protocol server modules into distinct layers: server lifecycle entrypoint, tool registration modules, and resource registration modules.
- Ensure service business logic and state managers remain fully decoupled from FastMCP decorators and transport objects.

## Continuation Context


Verify commands:
- Discover and execute the project's static analysis and linting verification scripts to validate protocol endpoint signatures and boundary constraints.
- Discover and execute the integration test suite targeting Model Context Protocol tool and resource contracts across supported transport modes.

Accept when:
- All Model Context Protocol tool endpoints and resource URIs respond according to declared contracts under automated verification suite execution.
- The protocol server successfully initializes and serves requests across both standard input-output and network transport modes without schema mismatch errors.

## Enforcement

- Verified by: Automated integration tests validating tool registration, resource resolution, and transport readiness.
- Verified by: Static analysis checks ensuring protocol layer code does not directly bypass service layer abstractions.
- Verified by: Peer code review during pull request inspection.
- Violation handling: Pull requests violating boundary separation or introducing unapproved transport layers will be blocked during automated verification.
- Violation handling: Deviations must be refactored to conform to standardized FastMCP registration patterns.
- Exception process: Exceptions require formal architectural review documenting why the standard protocol server framework cannot satisfy the integration requirements.
- Exception process: Approved exceptions must implement compatible protocol schemas to avoid breaking external agent integrations.