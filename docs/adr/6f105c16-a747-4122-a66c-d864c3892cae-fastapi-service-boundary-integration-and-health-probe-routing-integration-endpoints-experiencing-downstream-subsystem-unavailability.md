# FastAPI Service Boundary Integration and Health Probe Routing: Integration Endpoints Experiencing Downstream Subsystem Unavailability

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Distributed services and external adapters require deterministic integration contracts to validate inter-process connectivity, health status, and payload interchange.
- Disparate or undocumented endpoint topologies across services hinder integration verification and complicate automated dependency checking.
- Implementing standardized router interfaces ensures external adapters and background agent processors interact through uniform, discoverable boundary contracts.
- Centralized health probe endpoints provide explicit readiness and liveness signals necessary for integration test suites and orchestrator supervision.

## Problem Statement

Without standardized service boundary interfaces and uniform health verification endpoints, distributed components and adapters cannot reliably test integration status, validate payload transmission, or assert runtime readiness. Ad-hoc endpoint signatures create operational fragility, impede automated connectivity validation, and obscure integration failures between decoupled service subsystems.

## Decision

1. SHOULD: Integration endpoints experiencing downstream subsystem unavailability SHOULD raise standardized HTTP exceptions with explicit status codes indicating dependency readiness failures.

## Policy Block

- SHOULD Integration endpoints experiencing downstream subsystem unavailability SHOULD raise standardized HTTP exceptions with explicit status codes indicating dependency readiness failures.

In scope:
- All inter-service HTTP communication boundaries within the distributed application architecture.
- External adapter integration endpoints receiving asynchronous event signals or batch workloads.
- Service health and readiness probe implementations intended for integration verification and monitoring.

Out of scope:
- Internal intra-process function invocations and helper routines that do not traverse service network boundaries.
- Synchronous in-memory agent pipeline node transitions managed entirely within localized workflow state.

Exceptions:
- EXC-39-001: A service operates exclusively as an embedded sub-agent with no external network exposure or adapter communication requirements.

## Rationale

- Adopting FastAPI APIRouter contracts establishes predictable network interfaces that simplify integration testing across decoupled microservices and event adapters.
- Exposing uniform health and readiness probes enables automated configuration validators and test harnesses to confirm inter-service reachability prior to workload execution.
- Enforcing asynchronous handoff at integration endpoints prevents external adapter communication spikes from degrading core agent execution pipelines.

## Consequences

Positive:
- Uniform integration endpoints simplify end-to-end and contract testing across independent service components.
- Deterministic health probe interfaces allow deployment orchestrators and integration test runners to verify dependency readiness reliably.
- Decoupled router architectures isolate transport protocols from internal agent workflow execution.

Negative:
- Requires ongoing synchronization between published router contract schemas and external adapter client payload structures.
- Introduces HTTP layer overhead and serialization latency compared to direct in-memory event passing.
- Increases testing surface area by requiring validation of both transport route handlers and underlying workflow execution units.

## Alternatives

- Ad-hoc socket message passing without standardized HTTP router contracts (rejected)
  Rejected because: Lacks standardized schema validation, automated health probe conventions, and standard HTTP tooling integration, making distributed integration testing fragile and difficult to maintain.
  When valid: Valid only in ultra-low-latency real-time data streaming architectures with strict nanosecond budget requirements.
- Monolithic single-router service definition without modular APIRouter component separation (rejected)
  Rejected because: Creates tight coupling between disparate adapter domains and complicates targeted integration testing of isolated functional subsystems.
  When valid: Valid only in single-file proof-of-concept scripts with zero external integration boundaries.

## Risks

- Integration routes may accept unvalidated payload variations if client schemas drift from router parameter models.
  Mitigation: Enforce strict schema validation on all router endpoints and incorporate contract verification tests in the continuous integration pipeline.
  Owner: engineering team
- Health check endpoints may report healthy status while downstream dependencies or background task queues are stalled.
  Mitigation: Implement deep health verification logic within probe handlers that actively asserts downstream component availability.
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
- Separate route declaration modules from background service logic to facilitate isolated endpoint testing using simulated transport requests.
- Structure health check handlers to return consistent key-value dictionaries conveying operational status, capability inventories, and connection readiness.
- Ensure all integration handlers receive asynchronous background managers during application bootstrap rather than instantiating dependencies inside endpoint functions.

## Continuation Context


Verify commands:
- Discover the project test execution script and run the integration test suite targeting service routers and health probe endpoints.
- Discover the service configuration verification script and execute dependency reachability checks against all configured endpoints.

Accept when:
- All integration test suites targeting router endpoints and health probes execute to completion with zero failures.
- Service readiness and liveness endpoints respond with successful HTTP status codes and valid operational payload dictionaries.
- Boundary contract tests confirm that invalid or malformed incoming payloads are rejected with appropriate error responses.

## Enforcement

- Verified by: Continuous integration pipeline executing automated integration test suites and contract validation runs.
- Verified by: Peer code review verifying that new service boundaries expose compliant router instances and health probe endpoints.
- Violation handling: Pull requests lacking required health probes or router integration contracts are blocked from merging.
- Violation handling: Unvalidated endpoint schemas detected during automated verification trigger build failures requiring immediate remediation.
- Exception process: Submit an architectural deviation request detailing the specialized communication boundary constraints and obtain formal approval from the Architecture Review Board.