# CloudEvents Specification for Boundary Client Ingestion and Internal Agent Dispatch: Ingress Boundary Routes Not Discard Original

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- External boundary adapters and messaging clients ingest diverse asynchronous events that require routing and processing by internal agent orchestration services.
- Bespoke per-event HTTP submission endpoints created schema divergence and maintenance overhead across client commands and internal agent managers.
- A unified CloudEvents ingestion router was introduced to receive external client events without transport-level payload transformation, delegating domain classification to downstream agent monitor nodes.

## Problem Statement

External boundary adapters and messaging integrations generate heterogeneous event structures that historically required custom HTTP endpoints and fragmented payload handling. This caused coupling between boundary adapters and backend orchestration, introduced payload transformation discrepancies, and hindered end-to-end task lifecycle tracking across distributed services.

## Decision

1. MUST_NOT: Ingress boundary routes MUST NOT discard original CloudEvent attributes or transform domain payloads prior to task queuing.

## Policy Block

- MUST_NOT Ingress boundary routes MUST NOT discard original CloudEvent attributes or transform domain payloads prior to task queuing.

In scope:
- All external boundary adapters and client handlers transmitting asynchronous events to internal agent orchestration services.
- HTTP ingress routes receiving incoming notification, command, or lifecycle events from external platforms.

Out of scope:
- Synchronous query endpoints executing immediate in-process read operations.
- Intra-agent node transitions that do not cross service or adapter network boundaries.

Exceptions:
- EXC-001: Legacy batch task submission endpoints operating during documented deprecation transition phases.

## Rationale

- Adopting the CloudEvents specification provides a vendor-neutral, structured envelope for boundary events across disparate client adapters.
- Passing raw CloudEvent payloads directly to the agent queue without in-flight mutation eliminates transport data loss and preserves provenance context for lifecycle auditing.
- Centralizing event classification, context extraction, and priority assignment in dedicated monitor nodes maintains clean separation of concerns between HTTP ingress and agent processing.

## Consequences

Positive:
- Standardizes event ingestion contracts across heterogeneous external clients and boundary adapters using an open specification.
- Decouples external transport receipt from internal agent state transformation and execution scheduling.
- Preserves complete event provenance, original metadata, and raw context across task lifecycle tracking nodes.

Negative:
- Defers event classification and validation inside agent nodes, shifting payload parsing errors downstream from the HTTP ingress boundary.
- Introduces schema mapping maintenance overhead across external event type strings and internal trigger type enumerations.
- Increases message payload size due to CloudEvent envelope metadata encapsulation.

## Alternatives

- Bespoke HTTP Payload Ingestion Endpoints per Client Adapter (rejected)
  Rejected because: Creates tight coupling between ingress routes and external adapter schemas, requiring route modifications whenever an adapter adds or alters event structures.
  When valid: Applicable when an endpoint supports only a single proprietary client with immutable, non-standard event semantics.
- Adapter-Side Transformation into Internal Agent State Models (rejected)
  Rejected because: Leads to business logic leakage into external boundary clients and complicates event provenance tracking across distributed subsystems.
  When valid: Applicable in monolithic deployments where adapters share identical domain object models in-process.
- Direct Distributed Message Broker Ingestion (deferred)
  Rejected because: Introduces operational broker infrastructure overhead before traffic volume warrants replacing lightweight HTTP event ingestion.
  When valid: Applicable when sustained event throughput exceeds HTTP queuing capacity and requires partitioned stream persistence.

## Risks

- Schema drift between external client event types and internal trigger type enumerations causing unhandled events.
  Mitigation: Implement automated contract verification and schema checks to validate external event type strings against internal trigger mappings.
  Owner: engineering team
- Ingress queue exhaustion caused by unthrottled asynchronous CloudEvent bursts from boundary clients.
  Mitigation: Enforce queue backpressure and batch size limits at the ingestion boundary with health check monitoring.
  Owner: engineering team
- Downstream classification node failures triggered by malformed optional CloudEvent context attributes.
  Mitigation: Use defensive parser utilities that convert timestamps to UTC and supply default event contexts on parse exceptions.
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
- Ingress boundary endpoints must act as lightweight asynchronous task producers, delegating parsing, classification, and priority calculation to downstream nodes.
- Event monitor nodes must employ defensive context parsing with timezone-aware ISO timestamp handling and fallback trigger types for unrecognized event types.

## Continuation Context


Verify commands:
- bash -c 'eval "$(discover_contract_test_command)"'
- bash -c 'eval "$(discover_type_check_command)"'
- bash -c 'eval "$(discover_linter_command)"'

Accept when:
- All boundary client event emissions conform to the CloudEvents specification and pass contract validation tests.
- Event ingestion endpoints accept CloudEvent payloads without mutation and enqueue them directly into the agent task queue.
- Event monitor nodes classify CloudEvent types into internal trigger types with accurate priority assignment and lifecycle tracking.

## Enforcement

- Verified by: Automated contract and schema test suites validating ingress routes against CloudEvent specifications in continuous integration.
- Verified by: Static type analysis validating CloudEvent context models and internal trigger mappings across agent nodes.
- Verified by: Architectural peer review of all boundary integration and client adapter pull requests.
- Violation handling: Pull requests introducing non-CloudEvent payload contracts on boundary event ingestion endpoints will be rejected.
- Violation handling: Ingress routes discovered performing in-flight mutation on raw event payloads must be refactored to forward payloads as-is.
- Exception process: Submit an architectural exception request detailing technical blockers preventing CloudEvent compliance.
- Exception process: Obtain formal approval from the Architecture Review Board prior to deploying non-standard boundary integration endpoints.
- Exception process: Record an explicit deprecation timeline and migration milestone for any temporary legacy payload formats.