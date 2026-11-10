---
version: 2
name: 5488184a-ccd7-49bf-930c-f159d0542975-adoption-of-asyncio-for-asynchronous-runtime-and-task-concurrency-asynchronous-polling-intervals-retry-delays-use
description: "Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Asynchronous Polling Intervals Retry Delays Use"
metadata:
  actual:
    adr_id: 5488184a-ccd7-49bf-930c-f159d0542975
    status: accepted
    candidate_group_id: 78b32353-9b11-4b52-95e4-88d7e89116f5
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# Adoption of Asyncio for Asynchronous Runtime and Task Concurrency: Asynchronous Polling Intervals Retry Delays Use

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

## Context

- Multiple components across adapters, agent nodes, and service gateways require non-blocking I/O coordination for message handling and state polling.
- The application architecture relies on continuous background loops to monitor timers, CloudEvents, and external platform interactions.
- Standardizing on a single asynchronous foundation across all modules avoids fragmented concurrency models and thread synchronization hazards.

## Problem Statement

Coordinating multiple concurrent event streams, external adapter interactions, and autonomous agent loops without blocking execution or incurring heavy thread management overhead requires a unified asynchronous concurrency framework.

## Decision

1. SHOULD: Asynchronous polling intervals and retry delays SHOULD use asyncio.sleep rather than synchronous pauses to maintain cooperative multitasking.

## Policy Block

- SHOULD Asynchronous polling intervals and retry delays SHOULD use asyncio.sleep rather than synchronous pauses to maintain cooperative multitasking.

In scope:
- Network-bound event handling and message processing within service adapters.
- Agent execution node state transitions and continuous monitoring loops.
- Service gateway request routing and background maintenance tasks.

Out of scope:
- Dedicated CPU-bound computational workflows requiring separate process isolation.
- Standalone synchronous command-line utilities operating outside the main application runtime.

Exceptions:
- EXC-20-001: An external client library provides only synchronous blocking methods and no asynchronous alternative exists.

## Rationale

- Eleven files across adapters, agent nodes, and service layers consistently use asyncio for coroutine execution and task scheduling.
- Cooperative asynchronous scheduling prevents thread starvation and simplifies state management across concurrent event listeners.
- A unified asynchronous model ensures seamless composition between network adapters, messaging interfaces, and agent decision nodes.

## Consequences

Positive:
- Enables scalable, single-threaded cooperative multitasking across high-volume event streams without thread management complexity.
- Lowers memory footprint and context-switching overhead compared to thread-per-connection architectures.
- Provides deterministic control over task execution order, timeouts, and cancellation routines.

Negative:
- Developers must ensure blocking synchronous calls are not executed on the active event loop.
- Debugging coroutine deadlocks and tracing asynchronous task execution stacks requires specialized profiling techniques.
- Background tasks can fail silently if unhandled exceptions are not explicitly captured and logged.

## Alternatives

- Thread-based concurrency model (rejected)
  Rejected because: Preemptive multithreading introduces synchronization overhead, race condition risks, and higher memory footprints for I/O-bound event processing.
  When valid: Valid when integrating legacy blocking libraries that do not provide asynchronous interfaces.
- Multi-process worker pool model (rejected)
  Rejected because: Inter-process communication serialization cost and memory overhead are excessive for high-frequency lightweight event dispatching.
  When valid: Valid for isolated CPU-intensive computation or heavy machine learning tasks.

## Risks

- Unintended blocking operations on the event loop cause application-wide latency spikes.
  Mitigation: Enforce static analysis rules and peer review checks to detect synchronous network or filesystem operations inside coroutines.
  Owner: Engineering Team
- Unhandled exceptions in background tasks terminate silently without triggering recovery flows.
  Mitigation: Attach exception handlers and logging listeners to spawned background tasks to capture failures immediately.
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
- Structure continuous polling loops with clean shutdown logic that responds to cooperative cancellation.
- Isolate state mutations inside task boundaries and leverage asynchronous synchronization primitives where shared access is necessary.

## Continuation Context


Verify commands:
- Discover and run the project test suite using the repository test runner to validate coroutine lifecycle and non-blocking task execution.
- Execute repository static analysis and asynchronous linting checks to ensure proper coroutine awaiting and absence of blocking calls.

Accept when:
- All unit and integration tests executing asynchronous routines pass without unhandled task exceptions or event loop warnings.
- Static analysis confirms asynchronous invocations use proper awaiting without unhandled futures or stalled execution.

## Enforcement

- Verified by: Continuous integration pipelines executing asynchronous test suites.
- Verified by: Static analysis linters enforcing coroutine invocation rules and detecting unawaited futures.
- Verified by: Peer code review verifying task lifecycle management and cancellation handling.
- Violation handling: Code reviews reject pull requests introducing blocking calls into coroutine workflows.
- Violation handling: Automated test runs fail upon detecting unhandled exceptions within spawned background tasks.
- Exception process: Submit an architectural exception request detailing why asynchronous execution is impractical.
- Exception process: Demonstrate that blocking operations are offloaded to an executor pool and do not impact event loop responsiveness.