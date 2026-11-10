---
version: 2
name: a3578718-fb48-4989-979f-4cff1c68964d-adoption-of-requests-library-for-outbound-http-client-communication-components-requiring-synchronous-outbound-http-communication
description: "Adoption of Requests Library for Outbound HTTP Client Communication: Components Requiring Synchronous Outbound Http Communication"
metadata:
  actual:
    adr_id: a3578718-fb48-4989-979f-4cff1c68964d
    status: accepted
    candidate_group_id: 4cbbfdfb-5cbc-4110-ad26-c2cece0aac40
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/photo_vibe_check/**
---

# Adoption of Requests Library for Outbound HTTP Client Communication: Components Requiring Synchronous Outbound Http Communication

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/agents/ambient_event_agent/**`
- `tlt/mcp_services/photo_vibe_check/**`

## Context

- Multiple subsystems across service processors, adapter components, and agent validation routines require outbound HTTP communication to fetch remote assets, inspect health endpoints, and verify external service connectivity.
- Uncoordinated HTTP client usage and missing timeout boundaries risk worker thread starvation and cascading failures during external network latency spikes.
- Standardizing on the requests library provides a uniform, synchronous HTTP client interface with explicit configuration controls across modules.

## Problem Statement

Outbound HTTP calls executed without a standardized client abstraction or without mandatory timeout limits introduce risks of indefinite thread blocking, inconsistent error recovery, and fragmented connection lifecycle management across independent services.

## Decision

1. MUST: Components requiring synchronous outbound HTTP communication MUST adopt the requests library as the primary HTTP client abstraction.

## Policy Block

- MUST Components requiring synchronous outbound HTTP communication MUST adopt the requests library as the primary HTTP client abstraction.

In scope:
- All synchronous outbound HTTP network interactions originating from services, adapters, and agents.
- All configuration validation scripts verifying remote endpoint reachability.

Out of scope:
- Asynchronous event loop services utilizing native non-blocking HTTP protocols.
- Internal inter-process communication relying on non-HTTP transport mechanisms.

Exceptions:
- EXC-20-001: Specialized streaming or long-polling operations where static timeout boundaries disrupt continuous data feeds.

## Rationale

- Static analysis substantiates repeated adoption of requests across service processing, adapter monitoring, and configuration validation modules.
- Enforcing explicit timeout constraints on HTTP client requests prevents thread starvation and resource leaks when downstream endpoints experience degradation.
- A unified synchronous HTTP client abstraction simplifies dependency management and reduces maintenance overhead across the monorepo.

## Consequences

Positive:
- Consistent, human-readable API for outbound HTTP client requests across services, adapters, and validation utilities.
- Mandatory timeout parameters prevent silent thread hangs and connection pool exhaustion during remote network degradation.
- Simplified testing and mocking strategies across the monorepo by standardizing on a single synchronous HTTP client interface.

Negative:
- Synchronous network calls block the executing worker thread for the duration of the request up to the configured timeout limit.
- External library dependency requires continuous tracking of security advisories and upstream maintenance releases.

## Alternatives

- Standard library HTTP client modules (rejected)
  Rejected because: Standard library HTTP client abstractions require verbose boilerplate for connection management, parameter encoding, and response decoding across diverse services.
  When valid: Valid when external dependency installation is strictly prohibited or footprint constraints prevent external package adoption.
- Asynchronous HTTP client libraries (rejected)
  Rejected because: Introducing asynchronous event loops and client lifecycles across synchronous agent workers and validation scripts adds unnecessary concurrency complexity where synchronous workflows suffice.
  When valid: Valid when services require high-concurrency non-blocking I/O multiplexing across thousands of simultaneous external requests.

## Risks

- Thread exhaustion caused by slow downstream endpoints hanging synchronous HTTP requests.
  Mitigation: Enforce explicit timeout parameters on every outbound HTTP invocation through static analysis and automated test gates.
  Owner: Engineering Team
- Unhandled connection errors or HTTP status errors propagating unformatted exceptions into domain pipelines.
  Mitigation: Wrap requests network calls in structured exception handlers and return standardized error representations.
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
- Callers should encapsulate remote network interactions inside service boundaries and avoid leaking raw HTTP response structures into domain workflows.
- Timeout values must reflect downstream service service-level objectives, balancing fail-fast requirements with expected payload transfer durations.

## Continuation Context


Verify commands:
- Discover the repository test runner from project configuration and execute HTTP client test suites.
- Discover the repository static analysis and linting configuration to verify timeout parameter enforcement on requests calls.

Accept when:
- Static analysis and automated test suites confirm all outbound HTTP client calls specify explicit timeout parameters without unhandled blocking invocations.
- Automated test suites verify that remote network failures and timeout exceptions are gracefully handled by calling modules.

## Enforcement

- Verified by: Automated static analysis checks scanning repository source files for requests invocations missing timeout arguments.
- Verified by: Peer code review verifying outbound HTTP interactions conform to error handling and timeout standards.
- Violation handling: Code changes containing requests invocations without explicit timeout configurations are blocked during integration verification.
- Violation handling: Violations identified in existing modules must be remediated by supplying appropriate timeout boundaries and exception handling.
- Exception process: Exceptions must be submitted via architectural review requesting an exemption for specific high-concurrency workloads requiring asynchronous I/O.
- Exception process: Approved exceptions must document connection limits, timeout parameters, and boundary isolation mechanisms in local service documentation.