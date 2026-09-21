# Adoption of uvicorn as Core ASGI Server Runtime: Components Running Long Lived Background Protocols

Status: proposed
Date: 2025-07-02
Deciders: Detection Pipeline (automated)

## Context

- Service entrypoint modules and protocol adapters require an asynchronous server runtime to host HTTP endpoints and manage service lifecycles.
- Both adapter modules and core service entrypoints define public contract endpoints and require non-blocking asynchronous event handling.
- Static analysis detects shared adoption of uvicorn across entrypoint components within the service architecture.

## Problem Statement

Service components and external adapters need a uniform, high-performance asynchronous server runtime to host HTTP endpoints and orchestrate application lifespans without introducing conflicting hosting runtimes across the monorepo.

## Decision

1. SHOULD: Components running long-lived background protocols alongside the HTTP server SHOULD isolate background loops to prevent event loop contention.

## Policy Block

- SHOULD Components running long-lived background protocols alongside the HTTP server SHOULD isolate background loops to prevent event loop contention.

In scope:
- Backend services and adapters exposing network contracts or HTTP endpoints.
- Service entrypoints responsible for process lifecycle orchestration and ASGI interface hosting.

Out of scope:
- Internal helper modules and domain libraries that do not expose external network interfaces.
- Standalone batch processing scripts that run to completion without network listener loops.

## Rationale

- Adopting uvicorn provides a unified ASGI foundation across both service entrypoints and protocol adapters.
- Native ASGI support ensures seamless interoperation with modern asynchronous web frameworks and structured lifespan hooks.
- Consistent adoption across entrypoints simplifies operational deployment and container runtime standardization.

## Consequences

Positive:
- Standardizes asynchronous HTTP server runtime interfaces across service entrypoints and adapters.
- Enables native ASGI application lifecycle management and non-blocking endpoint execution.
- Provides consistent configuration integration for environment-driven runtime parameters.

Negative:
- Binds service execution lifecycles and concurrency handling to the event loop characteristics of the adopted ASGI server runtime.
- Requires explicit separation when running concurrent background listener threads alongside the asynchronous server loop.

## Alternatives

- Standard library synchronous HTTP server runtime (rejected)
  Rejected because: Lacks native asynchronous protocol support required for concurrent non-blocking operations and ASGI application lifecycles.
  When valid: Simple debugging utilities or isolated synchronous scripts with minimal concurrency requirements.
- Embedding separate independent web servers across each adapter without shared server runtime conventions (rejected)
  Rejected because: Introduces heterogeneous runtime behavior and complicates operational management across service entrypoints.
  When valid: Components interacting with third-party binary runtimes where custom server hosting cannot be controlled.

## Risks

- Event loop blocking caused by unmanaged synchronous execution within asynchronous request handlers.
  Mitigation: Isolate blocking background operations onto dedicated worker threads or external worker queues to prevent starvation of the event loop.
  Owner: engineering team
- Behavioral drift across minor server runtime updates impacting HTTP parsing or lifecycle hook dispatch.
  Mitigation: Enforce strict lock-file version resolution and execute integration smoke tests on dependency updates.
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
- Configure server instances through externalized environment sources rather than hardcoded configuration properties.
- Structure application lifespan contracts to manage clean resource initialization and shutdown alongside server execution.

## Continuation Context


Verify commands:
- Discover and run the project test runner script defined in the project configuration.
- Discover and execute the dependency audit script to verify declared server runtime dependencies against the lock artifact.
- Discover and run the static linter script across entrypoint modules to verify lifecycle compliance.

Accept when:
- The service entrypoint executes successfully and serves HTTP API routes via the configured ASGI server runtime.
- Static dependency and import analysis confirms that server lifecycle bindings conform to ASGI application contracts without direct process coupling violations.

## Enforcement

- Verified by: Continuous integration build pipelines verifying dependencies against the project lock artifact.
- Verified by: Automated static analysis and code review gates inspecting entrypoint server initialization.
- Violation handling: Build failures triggered during static analysis if undeclared or non-conforming server runtimes are introduced.
- Violation handling: Rejection of merge requests that bypass standardized ASGI lifecycle contracts.
- Exception process: Submit an architectural waiver request detailing specific protocol incompatibilities requiring an alternative server runtime.
- Exception process: Obtain documented approval from the technical architecture group before introducing non-standard server engines.