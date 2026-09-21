# asyncio Asynchronous Concurrency Architecture: Asynchronous Worker Routines Isolate Scheduled Intervals

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- The system coordinates concurrent event streams originating from external chat adapters, scheduled timers, and HTTP ingestion endpoints
- Operating system multi-threading models introduce substantial memory overhead and synchronization contention under sustained event traffic
- Cooperative multitasking via single-threaded asynchronous execution establishes structured task scheduling across agent nodes and service routers

## Problem Statement

Managing asynchronous event dispatching, timer evaluations, and network communication across distributed adapters and agent workflow nodes requires a concurrency model that scales without the overhead of operating system threads. Without a standardized asynchronous runtime pattern, blocking operations and inconsistent threading models risk thread exhaustion, race conditions, and deadlocks in event processing pipelines.

## Decision

1. SHOULD: Asynchronous worker routines SHOULD isolate scheduled intervals and task processing pipelines using cooperative non-blocking sleep and task queue primitives provided by the asynchronous runtime.

## Policy Block

- SHOULD Asynchronous worker routines SHOULD isolate scheduled intervals and task processing pipelines using cooperative non-blocking sleep and task queue primitives provided by the asynchronous runtime.

In scope:
- All message adapter handlers and network endpoint routers
- All agent state execution workflow nodes and background event monitoring loops
- All scheduled timer evaluations and asynchronous task dispatching pipelines

Out of scope:
- Purely computational data transformations and synchronous utility functions
- Isolated command-line migration scripts executing in synchronous batch mode

Exceptions:
- EXC-17-001: A third-party client library provides only synchronous blocking calls and cannot be replaced

## Rationale

- Static analysis confirms widespread adoption of asynchronous coroutine patterns across twenty-eight files spanning agent nodes, service routers, and external adapters
- The asyncio cooperative concurrency model delivers predictable, single-threaded execution that avoids race conditions on shared agent state dictionaries
- Asynchronous task queues and non-blocking timing primitives allow efficient scheduling and throttling of incoming platform events without thread contention

## Consequences

Positive:
- High-density concurrent I/O throughput achieved without the memory overhead of operating system threads
- Deterministic single-threaded cooperative scheduling eliminates mutual exclusion lock contention within coroutine state transitions
- Unified asynchronous paradigm across ingestion routers, background agent nodes, and platform message adapters

Negative:
- Any unhandled synchronous blocking call stalls the entire shared event loop thread and degrades system responsiveness
- Asynchronous call chains enforce contagious coroutine function signatures across all intermediate layers
- Debugging asynchronous stack traces and profiling event loops requires specialized diagnostic instrumentation

## Alternatives

- Multi-threaded concurrency utilizing operating system thread pools (rejected)
  Rejected because: Thread pools incur significant memory stack allocation per worker thread and introduce synchronization locking complexity prone to race conditions
  When valid: Workloads dominated by non-yielding CPU-bound tasks or synchronous native library bindings without asynchronous equivalents
- Process-based multiprocessing worker pools (rejected)
  Rejected because: Inter-process communication introduces high serialization overhead and memory footprint for lightweight event routing pipelines
  When valid: Heavy computational transformations or isolated CPU-intensive machine learning inference tasks

## Risks

- Accidental invocation of synchronous blocking functions within coroutines causing event loop starvation
  Mitigation: Enforce static analysis checks to detect blocking synchronous calls within coroutine definitions
  Owner: engineering team
- Unhandled exceptions inside background tasks leading to silent coroutine termination
  Mitigation: Implement structured task lifecycle management and centralized error logging for all detached tasks
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
- Utilize asynchronous queue primitives and non-blocking cooperative sleep functions for all polling loops and background agent cycles
- Wrap background task dispatching with centralized lifecycle state recording and local error capture to avoid unhandled task failures

## Continuation Context


Verify commands:
- Discover and run the project static analysis test suite to verify coroutine definitions and identify any unawaited calls
- Discover and execute the automated integration test suite to validate asynchronous event propagation across agent nodes

Accept when:
- All coroutines defined across event monitoring, routing, and adapter modules execute asynchronously without blocking the event loop
- Static concurrency verification verifies zero unawaited coroutine definitions across all service boundaries
- Automated test runs confirm that background tasks and scheduled timers process concurrently under active workloads

## Enforcement

- Verified by: Automated continuous integration pipeline running static analysis and coroutine linting checks
- Verified by: Peer code reviews validating that all network, file, and timer interactions utilize non-blocking asynchronous APIs
- Violation handling: Pull requests containing unawaited coroutines or blocking I/O calls within asynchronous contexts are blocked from merging
- Violation handling: Uncovered event loop blocking invocations detected in production environments require immediate remediation ticketing
- Exception process: Submit an architectural exception request detailing the required synchronous library integration and thread offloading strategy for review
- Exception process: Obtain sign-off from the technical lead prior to introducing dedicated worker thread executors in coroutine paths