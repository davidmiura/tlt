---
version: 2
name: 26bb83e5-279c-404d-9475-dd4e77c5f8a7-adoption-of-httpx-for-asynchronous-http-client-communication-before-implementing-updating-dependencies-involving-httpx
description: "Adoption of httpx for Asynchronous HTTP Client Communication: Before Implementing Updating Dependencies Involving Httpx"
metadata:
  actual:
    adr_id: 26bb83e5-279c-404d-9475-dd4e77c5f8a7
    status: accepted
    candidate_group_id: 4ba16875-5686-4b4a-88d5-dd99eac3ca39
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/clients/**
      - tlt/mcp_services/**
---

# Adoption of httpx for Asynchronous HTTP Client Communication: Before Implementing Updating Dependencies Involving Httpx

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/clients/**`
- `tlt/mcp_services/**`

## Context

- Service components and external adapters must communicate over HTTP with remote endpoints and internal microservices.
- Asynchronous runtimes require non-blocking I/O operations to maintain responsiveness and high concurrency under load.
- Unbounded network requests without explicit timeout configurations present operational failure modes and resource exhaustion risks.

## Problem Statement

Distributed service components and client adapters require outbound HTTP capabilities that integrate natively with asynchronous event loops without blocking concurrent execution, while guaranteeing bounded request latency through explicit timeout controls.

## Decision

1. MUST: Before implementing or updating dependencies involving httpx, the consumer MUST discover the project dependency lock artifact and verify the exact resolved version against official documentation.

## Policy Block

- MUST Before implementing or updating dependencies involving httpx, the consumer MUST discover the project dependency lock artifact and verify the exact resolved version against official documentation.

In scope:
- Asynchronous services, microservices, and protocol adapters initiating outbound HTTP requests.

Out of scope:
- In-process direct function calls, non-HTTP transport protocols, or isolated synchronous utility scripts operating outside the asynchronous event loop.

## Rationale

- Evidence from service and adapter implementations shows consistent adoption of httpx.AsyncClient for external client interactions.
- Configuring explicit timeouts prevents hung network sockets from cascading into widespread resource exhaustion.
- Standardizing on a unified asynchronous client library eliminates interface divergence across disparate adapters and services.

## Consequences

Positive:
- Non-blocking asynchronous HTTP requests preserve event loop concurrency across service and adapter runtimes.
- Standardized client instantiation establishes consistent timeout safeguards and request semantics across internal and external network boundaries.
- Enables uniform request and response handling patterns across distributed components.

Negative:
- Asynchronous client sessions require careful lifecycle and connection pool management to prevent socket exhaustion.
- Developers must consistently handle asynchronous client-specific exceptions across all calling contexts.

## Alternatives

- Synchronous HTTP client libraries (rejected)
  Rejected because: Synchronous socket operations block the runtime event loop during network latency, degrading throughput and responsiveness across asynchronous services.
  When valid: Valid only in isolated command-line scripts or purely synchronous batch workers where no asynchronous event loop is active.
- Alternative asynchronous client libraries with disparate interface designs (rejected)
  Rejected because: Introducing fragmented HTTP client libraries increases maintenance overhead and leads to inconsistent request, response, and error-handling semantics across services.
  When valid: Valid when an integration strictly requires specialized binary protocol features unsupported by the primary client library.

## Risks

- Connection pool leakage or socket exhaustion resulting from repeated unclosed client instantiations.
  Mitigation: Reuse client instances or manage them via asynchronous context managers to ensure socket closure and connection pool recycling.
  Owner: engineering team
- Cascading service degradation caused by unconfigured or overly permissive request timeouts.
  Mitigation: Enforce static analysis checks requiring non-null timeout values on all client constructor invocations.
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
- Instantiate client sessions using structured lifecycle management or long-lived shared instances to benefit from connection pooling.
- Define explicit timeout values calibrated to the latency expectations of downstream dependencies rather than accepting infinite waits.

## Continuation Context


Verify commands:
- Discover and run the project static analysis and linting scripts to verify that HTTP client instantiations use httpx.AsyncClient with explicit timeout parameters.
- Discover and run the project automated test suite to validate asynchronous HTTP client communication across service and adapter boundaries.

Accept when:
- Static analysis confirms all outbound HTTP client instantiations across services and adapters utilize httpx.AsyncClient with explicit timeout configurations.
- Automated test suites validate non-blocking asynchronous request execution and graceful handling of network timeouts.

## Enforcement

- Verified by: Automated static analysis and linting rules executed in continuous integration pipelines.
- Verified by: Peer code review verifying client instantiation patterns and timeout parameters.
- Violation handling: Pull requests introducing non-standard or synchronous HTTP client calls in asynchronous boundaries are blocked.
- Violation handling: Detected violations must be refactored to use httpx.AsyncClient before deployment approval.
- Exception process: Submit an architectural exception request documenting why the standard asynchronous client cannot satisfy the protocol requirements.
- Exception process: Obtain sign-off from the technical lead before merging synchronous or non-standard networking implementations.