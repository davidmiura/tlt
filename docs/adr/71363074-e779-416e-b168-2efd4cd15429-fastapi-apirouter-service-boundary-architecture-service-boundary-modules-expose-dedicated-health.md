---
version: 2
name: 71363074-e779-416e-b168-2efd4cd15429-fastapi-apirouter-service-boundary-architecture-service-boundary-modules-expose-dedicated-health
description: "FastAPI APIRouter Service Boundary Architecture: Service Boundary Modules Expose Dedicated Health"
metadata:
  actual:
    adr_id: 71363074-e779-416e-b168-2efd4cd15429
    status: accepted
    candidate_group_id: a0b3689c-1ef1-4735-b714-080fde0d23b2
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# FastAPI APIRouter Service Boundary Architecture: Service Boundary Modules Expose Dedicated Health

Status: proposed
Date: 2025-07-02
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/mcp_services/**`
- `tlt/services/tlt_service/**`

## Context

- Service adapters and backend domain modules must expose structured HTTP endpoints for external webhooks, event ingestion, and inter-service coordination.
- Without a unified boundary definition mechanism, routing logic and request handling risk fragmentation across disparate HTTP abstractions and ad-hoc request parsers.
- The monorepo requires modular route isolation where individual domain capabilities define self-contained routing controllers that attach into parent application contexts.
- Explicit schema contracts and standardized HTTP status handling are necessary to maintain boundary contracts between external adapters and internal domain services.

## Problem Statement

Decentralized service communication and multi-adapter event handling require consistent HTTP route declarations, payload serialization, and boundary isolation across disparate modules. Without a standardized boundary architecture, adapter layers and internal services accumulate divergent routing patterns, inconsistent status code handling, and implicit contract definitions that degrade service maintainability and boundary clarity.

## Decision

1. SHOULD: Service boundary modules SHOULD expose dedicated health check and operational monitoring routes to report readiness and subsystem connectivity.

## Policy Block

- SHOULD Service boundary modules SHOULD expose dedicated health check and operational monitoring routes to report readiness and subsystem connectivity.

In scope:
- All HTTP endpoint controllers and route definitions across service adapters and core services.
- External webhook receivers and event ingestion boundaries.
- Operational monitoring and health check endpoint declarations.

Out of scope:
- Internal domain logic and computation workflows executing outside HTTP transport boundaries.
- Standalone CLI utilities and background thread execution loops that do not expose network endpoints.

Exceptions:
- EXC-23-001: A specialized protocol server or transport mechanism requires a native non-HTTP network socket listener.

## Rationale

- Standardizing on FastAPI APIRouter provides modular, composable boundary definitions across diverse service adapters and domain components without tight coupling to server startup logic.
- Enforcing typed request and response models guarantees structural schema validation at network boundaries, preventing malformed external payloads from penetrating domain layers.
- Uniform HTTP exception modeling guarantees predictable error responses and status semantics across all adapter integrations and monitoring clients.

## Consequences

Positive:
- Modular route organization enables clean domain boundary separation and independent router maintenance across adapters.
- Declarative response models and schema validation provide automatic request validation and predictable contract shapes.
- Standardized status code handling and health check endpoints simplify monitoring and operational observability.

Negative:
- Couples service transport boundaries tightly to framework-specific routing abstractions and schema validation conventions.
- Requires explicit schema maintenance for every endpoint payload and response structure, increasing initial definition overhead.

## Alternatives

- Monolithic Application Route Definitions (rejected)
  Rejected because: Binding route definitions directly to a single global application instance creates tight architectural coupling between unrelated adapters and impairs modular domain decomposition.
  When valid: Valid only in single-file utility scripts with no distinct domain modules or external adapters.
- Untyped Raw Request Handlers (rejected)
  Rejected because: Lacks automated payload validation, typed serialization contracts, and declarative route modeling, requiring extensive boilerplate error checking in every handler.
  When valid: Valid when implementing custom low-level protocol gateways requiring raw byte stream handling.

## Risks

- Domain models leaking directly into public boundary response schemas, coupling internal persistence state to external contracts.
  Mitigation: Enforce strict separation between internal domain entities and boundary response models at the router interface.
  Owner: Engineering Team
- Unhandled synchronous blocking operations inside asynchronous route coroutines degrading overall server concurrency.
  Mitigation: Ensure all blocking external operations and synchronous computations are delegated to worker pools or asynchronous adapters.
  Owner: Engineering Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Organize routers by cohesive domain resource or adapter capability, and register them onto the root application context using route prefixes and tags.
- Ensure all endpoint error conditions map to standardized framework HTTP exceptions with informative detail fields rather than untyped server exceptions.

## Continuation Context


Verify commands:
- Discover the workspace test execution framework from repository configuration and run the route integration and contract test suites.
- Locate the workspace static analysis and type checking utilities from the project configuration and execute them across all route boundary definitions.

Accept when:
- All boundary route handlers pass integration tests with valid and invalid payloads according to declared schema contracts.
- Static type analysis and contract validation verify zero type discrepancies between router definitions and declared response models.
- Operational and health monitoring endpoints respond with valid status payloads across all service boundary components.

## Enforcement

- Verified by: Automated continuous integration test suites verifying endpoint status codes and schema contracts.
- Verified by: Static type analysis and schema validation checks executed during pipeline verification.
- Verified by: Peer code review auditing route modularity and response model declarations.
- Violation handling: Pull requests containing untyped route handlers or unhandled exception patterns will fail automated verification.
- Violation handling: Non-compliant endpoints must be refactored to use modular routers and typed schemas before merge.
- Exception process: Submit an architectural exception proposal specifying protocol constraints that prevent standard router adoption, subject to team lead approval.