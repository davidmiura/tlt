---
version: 2
name: f65f48f9-ffe5-42a9-8cc6-9faf9dbbf63a-cloudevents-ingress-protocol-adoption-via-tlt-shared-cloudevents-before-implementing-updating-any-event-serialization
description: "CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Before Implementing Updating Any Event Serialization"
metadata:
  actual:
    adr_id: f65f48f9-ffe5-42a9-8cc6-9faf9dbbf63a
    status: accepted
    candidate_group_id: a6f6f686-17bf-4352-9cfd-e3550d75d771
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# CloudEvents Ingress Protocol Adoption via tlt.shared.cloudevents: Before Implementing Updating Any Event Serialization

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/agents/ambient_event_agent/**`
- `tlt/mcp_services/**`
- `tlt/scripts/**`
- `tlt/services/tlt_service/**`
- `tlt/shared/**`

## Context

- External integration adapters, such as Discord bot adapters and automated event monitors, communicate with the platform via public HTTP service endpoints.
- Public event endpoints previously utilized divergent payload formats and direct task submission endpoints, creating coupling between external event adapters and internal agent task models.
- Adopting a standardized protocol envelope at public ingress boundaries allows the platform to accept heterogeneous event types through a single unified ingress endpoint.

## Problem Statement

Inconsistent data formats across external adapters and boundary integrations lead to fragile parsing logic, tight coupling between external event sources and internal workflows, and lack of standardized metadata for tracing and priority routing.

## Decision

1. MUST: Before implementing or updating any event serialization or routing dependencies, developers MUST inspect the repository lock artifact to determine the exact resolved dependency version and verify that all invoked interfaces match that resolved specification.

## Policy Block

- MUST Before implementing or updating any event serialization or routing dependencies, developers MUST inspect the repository lock artifact to determine the exact resolved dependency version and verify that all invoked interfaces match that resolved specification.

In scope:
- All public HTTP endpoints accepting asynchronous external events and adapter notifications.
- External adapters and boundary services publishing events into the core platform services.
- Internal event ingestion and classification nodes routing incoming adapter events.

Out of scope:
- Synchronous health checks, status reporting, and administrative resource queries.
- Private inter-node state transitions contained entirely within isolated agent state machines.

## Rationale

- Static code evidence in public ingress routing demonstrates a dedicated endpoint enforcing CloudEvent envelope validation while passing payloads without mutation directly into asynchronous processing queues.
- Downstream agent nodes explicitly inspect standard envelope attributes (type, source, id, subject, time) to classify events and extract execution contexts, proving centralized protocol standardization.
- Standardizing on the shared CloudEvent schema across boundary services establishes clear interoperability boundaries between external client adapters and internal workflow orchestrators.

## Consequences

Positive:
- Provides a uniform, standardized ingestion contract for all external integration adapters and third-party event producers.
- Enables payload-agnostic queuing, routing, and audit logging at public service ingress without payload transformation.
- Standardizes event identification, source provenance, timestamping, and priority classification across disparate event sources.

Negative:
- Enforces envelope serialization overhead and nesting of domain data within transport wrappers across all ingress boundaries.
- Requires downstream processing nodes to maintain explicit classification mappings for every supported event type identifier.

## Alternatives

- Ad-hoc proprietary JSON payloads for each external integration endpoint (rejected)
  Rejected because: Creates fragmented schema validation, tight coupling between external adapters and internal services, and bespoke routing logic for every external event source.
  When valid: Valid only for isolated internal prototyping where no external adapters or multi-tenant event streams exist.
- Direct RPC or synchronous task invocation across boundary adapters (rejected)
  Rejected because: Ties external adapter responsiveness to internal agent processing latency and creates cascading failures during service degradation.
  When valid: Valid only for strictly synchronous read queries where immediate execution results are required by the external caller.

## Risks

- New external event types may be dropped or misclassified if event type mappings are not kept in sync with adapter capabilities.
  Mitigation: Provide comprehensive fallback trigger mappings and preserve raw payload dictionaries during classification so unmapped event types remain accessible for subsequent handling.
  Owner: engineering team
- Large nested data payloads within envelopes may introduce memory pressure during batch queuing and state transitions.
  Mitigation: Enforce payload size limits at the ingress gateway and design event payloads to pass entity identifiers rather than large binary blobs.
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
- Ensure public ingress routers operate as pass-through queues, forwarding valid envelopes directly into agent task queues without schema transformation.
- Ensure event classification functions gracefully fall back to generic event triggers when receiving unknown event type identifiers while preserving all raw payload attributes.

## Continuation Context


Verify commands:
- Discover the project test runner from repository configuration manifests and execute the test suite covering public event ingress routing and schema validation.
- Locate the linter and static type verification scripts from the project configuration and execute them across the shared event modules and routing packages.

Accept when:
- Public HTTP event ingress routes accept valid CloudEvent envelopes and successfully enqueue corresponding asynchronous processing tasks.
- Invalid event payloads lacking required envelope attributes are rejected at the ingress boundary with appropriate client error responses.
- Downstream event monitoring components successfully classify event type descriptors into internal trigger types without loss of context metadata.

## Enforcement

- Verified by: Automated contract and schema validation test suites executed during continuous integration.
- Verified by: Static analysis rules verifying that public event ingress handlers consume the shared CloudEvent data model.
- Verified by: Peer review of public API route additions and adapter integration changes.
- Violation handling: Pull requests introducing non-standard public event endpoints or direct payload transformations at ingress are blocked at review.
- Violation handling: Runtime requests to public event ingress routes lacking mandatory envelope attributes fail schema validation and return client error statuses.
- Exception process: Exceptions to the standardized event envelope contract must be submitted as architectural change requests detailing technical constraints preventing envelope encapsulation.
- Exception process: Temporary exceptions require approval from the principal integration architect and must define an adapter migration plan with an expiration date.