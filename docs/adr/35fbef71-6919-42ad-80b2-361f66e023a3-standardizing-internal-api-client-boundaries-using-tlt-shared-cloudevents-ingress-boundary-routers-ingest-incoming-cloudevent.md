---
version: 2
name: 35fbef71-6919-42ad-80b2-361f66e023a3-standardizing-internal-api-client-boundaries-using-tlt-shared-cloudevents-ingress-boundary-routers-ingest-incoming-cloudevent
description: "Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Ingress Boundary Routers Ingest Incoming Cloudevent"
metadata:
  actual:
    adr_id: 35fbef71-6919-42ad-80b2-361f66e023a3
    status: accepted
    candidate_group_id: 4bdbe324-bdbd-46cc-b3c9-4ba5cff2bd7c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Standardizing Internal API Client Boundaries Using tlt.shared.cloudevents: Ingress Boundary Routers Ingest Incoming Cloudevent

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/agents/ambient_event_agent/**`
- `tlt/mcp_services/**`
- `tlt/services/tlt_service/**`
- `tlt/shared/**`

## Context

- External client adapters and platform ingress points receive diverse notifications, webhook triggers, and interaction events from multiple boundary sources.
- Direct point-to-point payload passing creates tight coupling between external event schemas and internal agent task models.
- Standardizing internal boundary ingress on an immutable event envelope ensures uniform auditability and asynchronous queue compatibility across monorepo services.

## Problem Statement

Heterogeneous external client adapters and boundary ingress endpoints historically utilized divergent, point-to-point request schemas when forwarding events to internal services, causing tight coupling, fragile task routing, and payload drift across asynchronous processing boundaries.

## Decision

1. MUST: Ingress boundary routers MUST ingest incoming CloudEvent instances without mutating or transforming the payload data prior to asynchronous queue dispatch.

## Policy Block

- MUST Ingress boundary routers MUST ingest incoming CloudEvent instances without mutating or transforming the payload data prior to asynchronous queue dispatch.

In scope:
- All external client adapters communicating asynchronously with internal services
- All boundary ingress endpoints accepting external event notifications or triggers
- All background task dispatchers handling external client events

Out of scope:
- Internal synchronous queries that do not cross service boundary contexts
- Ephemeral intra-process utility function calls within a single module

Exceptions:
- EXC-001: Synchronous high-throughput health checks and diagnostic telemetry endpoints

## Rationale

- Shared CloudEvent data models provide standardized metadata fields for event identification, source provenance, event typing, and payload encapsulation.
- Preserving raw event payloads without intermediate transformation at ingress routers guarantees data integrity during task queueing and agent state hydration.
- Downstream event classification nodes can reliably map standardized event types to specific internal domain triggers without custom adapter logic for each boundary source.

## Consequences

Positive:
- Decouples external client adapters from internal service state machines and background agents.
- Establishes standard event provenance, tracking identifiers, and timestamps across heterogeneous event sources.
- Prevents payload schema corruption at boundary ingress points through untransformed pass-through dispatch.

Negative:
- Introduces contract dependency overhead across external adapter and internal consumer modules.
- Requires event classification and mapping steps inside downstream processing nodes before domain execution.

## Alternatives

- Point-to-point bespoke request payloads per external adapter (rejected)
  Rejected because: Introduces tight coupling between external adapters and internal consumers, requiring bespoke deserializers and increasing schema drift across boundary integrations.
  When valid: Valid only in throwaway prototypes with a single external client.
- Synchronous RPC endpoints with domain-specific request bodies (rejected)
  Rejected because: Precludes asynchronous task queuing and prevents decoupling long-running agent workflows from external client response cycles.
  When valid: Valid for low-latency synchronous data retrieval queries requiring immediate response data.

## Risks

- External adapters may emit malformed event metadata attributes resulting in downstream event classification failures.
  Mitigation: Validate CloudEvent structure at the ingress boundary and return standard error responses before queuing tasks.
  Owner: Platform Engineering
- Schema evolution in shared event structures could introduce breaking changes across distributed internal services.
  Mitigation: Enforce additive schema changes and backward-compatible model extensions within the shared contract library.
  Owner: Integration Architecture

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Ensure that external adapter clients serialize outgoing messages using the shared contract classes provided by the internal event module.
- Configure ingress boundary routers to pass deserialized event models directly to task managers without modifying inner payload dictionaries.
- Implement exhaustive event classification in downstream consumer nodes to route unknown event types gracefully without terminating processing loops.

## Continuation Context


Verify commands:
- Discover the project test runner configured in the dependency manifest and execute the boundary integration test suite.
- Discover the project static type checker and run type verification on all boundary routing modules.
- Discover the contract verification task in the project configuration and execute schema compliance checks.

Accept when:
- All ingress boundary endpoints accept and validate event payloads conforming to the shared event contract.
- Asynchronous task queues receive unmodified event instances with intact metadata attributes.
- All automated boundary verification and type checking suites pass without contract violations.

## Enforcement

- Verified by: Automated continuous integration contract tests validating boundary request schemas
- Verified by: Static type analysis and schema compatibility linters executed in continuous integration
- Verified by: Peer code review for all new external adapter and ingress router implementations
- Violation handling: Pull requests introducing unencapsulated boundary payloads or mutated event structures are blocked by continuous integration.
- Violation handling: Boundary endpoints accepting unstandardized payloads must be refactored prior to deployment.
- Exception process: Submit an architecture review request detailing the boundary constraints and technical rationale for non-standard payload structures.