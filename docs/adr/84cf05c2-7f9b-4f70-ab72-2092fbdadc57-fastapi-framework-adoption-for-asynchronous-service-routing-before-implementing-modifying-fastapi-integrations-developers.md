---
version: 2
name: 84cf05c2-7f9b-4f70-ab72-2092fbdadc57-fastapi-framework-adoption-for-asynchronous-service-routing-before-implementing-modifying-fastapi-integrations-developers
description: "FastAPI Framework Adoption for Asynchronous Service Routing: Before Implementing Modifying Fastapi Integrations Developers"
metadata:
  actual:
    adr_id: 84cf05c2-7f9b-4f70-ab72-2092fbdadc57
    status: accepted
    candidate_group_id: 73cf1c92-ceb9-46c1-b474-e7cb2b21dc44
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/mcp_services/event_manager/**
      - tlt/services/tlt_service/**
---

# FastAPI Framework Adoption for Asynchronous Service Routing: Before Implementing Modifying Fastapi Integrations Developers

Status: proposed
Date: 2025-07-02
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/mcp_services/event_manager/**`
- `tlt/services/tlt_service/**`

## Context

- The repository implements multiple services, adapters, and model context protocol services that expose HTTP interfaces for health monitoring, task management, and event ingestion.
- External integrations and background agents operate on asynchronous event loops requiring non-blocking HTTP handling to prevent latency bottlenecks.
- Modular organization is required across service domains to allow independent definition and testing of route collections.

## Problem Statement

Services and adapters across the repository require a standardized, non-blocking HTTP transport layer that provides modular routing, request parsing, and error signaling without blocking asynchronous event loops.

## Decision

1. MUST: Before implementing or modifying FastAPI integrations, developers MUST consult the repository dependency manifest and inspect the authoritative lock artifact to verify the exact resolved version against public documentation.

## Policy Block

- MUST Before implementing or modifying FastAPI integrations, developers MUST consult the repository dependency manifest and inspect the authoritative lock artifact to verify the exact resolved version against public documentation.

In scope:
- All HTTP service endpoints, ingress adapters, and protocol service routes within the repository.
- All health check, metrics monitoring, and event ingestion handlers exposing HTTP transports.

Out of scope:
- Internal message queue workers and background agents that do not expose HTTP interfaces.
- Pure domain logic, data models, and standalone utility scripts that operate independently of HTTP transport.

## Rationale

- FastAPI provides native asynchronous route handling compatible with event loop concurrency requirements across bot adapters and background services.
- Modular APIRouter components permit domain-specific route grouping, maintaining clear architectural boundaries between adapters, monitoring, and event management.
- Uniform HTTP routing mechanics reduce cognitive load and avoid fragmented transport patterns across disparate service modules.

## Consequences

Positive:
- Establishes consistent, modular endpoint declarations across adapters and services using isolated routing components.
- Enables non-blocking asynchronous request handling aligned with event-driven bot adapters and task queues.
- Provides automated request validation and schema enforcement at service ingress boundaries.

Negative:
- Tightly binds transport layer route handlers to framework-specific routing interfaces and HTTP exception types.
- Unintentional synchronous blocking calls inside route handler coroutines risk starving the underlying asynchronous event loop.

## Alternatives

- Synchronous WSGI web frameworks (rejected)
  Rejected because: Incompatible with the asynchronous concurrency model required by real-time event adapters and background task queues.
  When valid: Viable only for isolated synchronous batch tasks or legacy services with no concurrent event loops.
- Direct route registration on a single root application instance (rejected)
  Rejected because: Couples independent adapter and service domains into a monolithic configuration, impairing modular maintenance and test isolation.
  When valid: Acceptable only in single-file microservices with minimal routing requirements.

## Risks

- Synchronous blocking operations within asynchronous route handlers can degrade overall service throughput.
  Mitigation: Enforce asynchronous operations for I/O and offload CPU-intensive operations to background tasks or worker pools.
  Owner: engineering team
- Tight coupling of domain logic to web framework transport types and exception structures.
  Mitigation: Maintain clean separation between transport route handlers and underlying domain service logic.
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
- Register modular route collections onto the root service application during lifecycle startup rather than directly declaring endpoints on the root instance.
- Ensure all network interactions and downstream queue dispatches within route handlers are awaited to preserve event loop concurrency.

## Continuation Context


Verify commands:
- Discover the repository test execution script and run the automated integration test suite covering API route declarations.
- Discover the repository static analysis script and verify type compatibility and route decorator compliance across all API modules.

Accept when:
- All automated test suites for route handlers, schema validation, and health check endpoints pass with zero failures.
- Static analysis checks verify that all public HTTP endpoints use framework route decorators without signature violations.

## Enforcement

- Verified by: Automated continuous integration test suites verifying route responses and status codes.
- Verified by: Static analysis checking for non-compliant routing patterns during pull request reviews.
- Violation handling: Build failures in continuous integration pipelines for unhandled exceptions or invalid route contracts.
- Violation handling: Code review rejection for endpoints declared outside modular router structures.
- Exception process: Exceptions must be submitted via architectural review request documenting why asynchronous routing is unsuitable for the specific component.