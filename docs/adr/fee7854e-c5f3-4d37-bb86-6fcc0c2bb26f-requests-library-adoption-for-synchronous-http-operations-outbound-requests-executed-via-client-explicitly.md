# Requests Library Adoption for Synchronous HTTP Operations: Outbound Requests Executed Via Client Explicitly

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Multiple discrete subsystems across agents, adapters, and microservices require outbound HTTP connectivity to retrieve external assets, validate endpoint availability, and query external APIs.
- Ad-hoc HTTP client implementations risk inconsistent timeout configurations, thread starvation, and divergent error recovery behaviors across service boundaries.
- Static analysis confirms recurring adoption of the requests library across multiple repository modules for synchronous network communication.

## Problem Statement

Without a standardized client for synchronous outbound HTTP operations, individual services risk adopting disparate networking primitives with inconsistent timeout configurations, missing failure handling, and unmanaged connection resources, leading to potential process starvation during network partitions.

## Decision

1. MUST: All outbound requests executed via the client MUST explicitly specify a timeout parameter to prevent indefinite thread blocking on network operations.

## Policy Block

- MUST All outbound requests executed via the client MUST explicitly specify a timeout parameter to prevent indefinite thread blocking on network operations.

In scope:
- Synchronous outbound HTTP requests executed across service boundaries.
- External service connectivity validation and resource download tasks in worker processes.

Out of scope:
- High-concurrency asynchronous workflows requiring native non-blocking event loop integration.
- Internal in-memory inter-process communications.

Exceptions:
- EXC-20-001: A service component operates entirely within an asynchronous event loop requiring native non-blocking asynchronous HTTP client drivers.

## Rationale

- Standardizing on the requests library provides a mature, reliable synchronous HTTP client interface across backend service boundaries.
- Enforcing explicit timeout configurations across all requests calls mitigates network partition risks and prevents process starvation.
- Centralizing on a single synchronous HTTP client abstraction simplifies integration testing, contract verification, and operational dependency maintenance.

## Consequences

Positive:
- Consistent timeout policies and error boundaries across all synchronous external HTTP interactions.
- Reduced cognitive overhead across agent, adapter, and microservice subsystems through a unified client API.
- Standardized mock and contract testing patterns for network boundaries.

Negative:
- Synchronous blocking calls can degrade throughput if inadvertently introduced into asynchronous event loops without offloading to worker threads.
- Requires disciplined governance to prevent unconfigured connection pools and unhandled network failure modes.

## Alternatives

- Standard library HTTP client modules without third-party dependencies (rejected)
  Rejected because: Standard library primitives require significant boilerplate for connection pooling, certificate verification, and timeout management.
  When valid: Valid in constrained runtime environments where zero external package installations are permitted.
- Mandatory asynchronous HTTP client adoption across all service boundaries (rejected)
  Rejected because: Asynchronous clients introduce unnecessary complexity for synchronous validation scripts, sequential batch processors, and single-purpose utilities.
  When valid: Valid within high-throughput asynchronous services requiring multiplexed concurrent I/O.

## Risks

- Blocking the main execution thread during slow upstream responses if timeouts are omitted or improperly configured
  Mitigation: Enforce mandatory timeout parameters on all client calls via static code analysis rules and automated verification.
  Owner: Engineering Team
- Accidental invocation of synchronous HTTP methods inside asynchronous event loops causing event loop latency spikes
  Mitigation: Verify runtime execution contexts and execute synchronous requests calls within dedicated thread pool executors when invoked from asynchronous functions.
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
- Always supply explicit timeout values representing connect and read limits on every network invocation.
- When executing repetitive requests against the same remote host, instantiate and reuse a client session instance to benefit from connection pooling.

## Continuation Context


Verify commands:
- Discover and execute the project static analysis suite to verify that all external HTTP invocations supply an explicit timeout argument.
- Discover and run the project test runner to execute unit and integration test suites validating external client error handling and response parsing.

Accept when:
- All synchronous outbound HTTP invocations specify an explicit timeout parameter.
- Project test suites mocking external HTTP client responses pass without unhandled network exceptions.
- Repository lock artifact inspection confirms the resolved HTTP client version satisfies project dependency constraints.

## Enforcement

- Verified by: Automated static analysis checks in continuous integration pipelines.
- Verified by: Peer code review verification against network boundary rules.
- Violation handling: Pull requests containing synchronous HTTP calls without explicit timeouts or unapproved client libraries will be blocked from merging.
- Violation handling: Code review feedback will require refactoring invocations to comply with standardized client patterns.
- Exception process: Submit an architectural exception request detailing why the standard synchronous client cannot satisfy latency or concurrency constraints, subject to review board approval.