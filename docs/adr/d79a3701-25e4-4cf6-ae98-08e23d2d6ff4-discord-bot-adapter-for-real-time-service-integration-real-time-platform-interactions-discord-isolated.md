---
version: 2
name: d79a3701-25e4-4cf6-ae98-08e23d2d6ff4-discord-bot-adapter-for-real-time-service-integration-real-time-platform-interactions-discord-isolated
description: "Discord Bot Adapter for Real-Time Service Integration: Real Time Platform Interactions Discord Isolated"
metadata:
  actual:
    adr_id: d79a3701-25e4-4cf6-ae98-08e23d2d6ff4
    status: accepted
    candidate_group_id: e4afcc1b-6f1f-40c0-a177-723e8f843814
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Discord Bot Adapter for Real-Time Service Integration: Real Time Platform Interactions Discord Isolated

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`

## Context

- The application integrates real-time chat platform messaging, thread management, and event interactions with backend service workflows.
- Interfacing directly with third-party real-time gateways risks coupling domain business rules to connection lifecycle events and rate limits.
- A modular adapter boundary is required to mediate between incoming HTTP trigger requests, periodic background state queries, and outbound real-time gateway dispatches.

## Problem Statement

Directly invoking third-party chat gateway protocols from disparate business services creates brittle dependencies on gateway connection states, leaks platform-specific data formats, and complicates error handling and rate-limit governance across the platform.

## Decision

1. MUST: All real-time platform interactions with Discord MUST be isolated within dedicated adapter components subclassing the platform bot command client, separating gateway lifecycle management from internal service domain logic.

## Policy Block

- MUST All real-time platform interactions with Discord MUST be isolated within dedicated adapter components subclassing the platform bot command client, separating gateway lifecycle management from internal service domain logic.

In scope:
- Services integrating bidirectional real-time communications with Discord chat gateways.
- Adapter components managing event threads, channel messaging, and direct message interactions.

Out of scope:
- Internal inter-service synchronous HTTP communications that do not touch chat platform gateways.
- Batch processing pipelines operating purely on persisted database records.

## Rationale

- Encapsulating chat platform client interactions within a dedicated adapter ensures gateway connection lifecycles remain decoupled from core domain services.
- Delegating interaction events to specialized bridge handlers facilitates maintainable, independently testable integration paths.
- Validating inbound payloads via typed schemas prevents invalid parameters from causing runtime exceptions during asynchronous chat dispatches.

## Consequences

Positive:
- Isolates third-party real-time chat protocol dependencies and session management from internal domain logic.
- Enables consistent schema validation on incoming platform trigger requests before dispatching chat messages.
- Provides modular delegation of chat interactions to specialized bridge and handler components.

Negative:
- Requires managing asynchronous gateway state synchronization loops alongside REST service lifecycles.
- Introduces susceptibility to chat platform rate limits that demand dedicated backoff and queuing strategies.

## Alternatives

- Direct platform client invocation from business domain services (rejected)
  Rejected because: Tightly couples core domain logic to third-party chat gateway protocols and connection lifecycles.
  When valid: Single-script prototypes or standalone command-line utilities.
- Webhook-only outward notifications without gateway client connection (rejected)
  Rejected because: Lacks support for bidirectional interactions, thread creation, reactions, and direct user messaging.
  When valid: Passive notification-only alert sinks with no user interaction requirements.

## Risks

- Chat platform API rate limits or network partitions may drop outbound notifications.
  Mitigation: Wrap message dispatch invocations in try-except blocks with exponential backoff and localized queueing.
  Owner: Integration Engineering Team
- Gateway connection drops could silently halt background event monitoring and dispatch tasks.
  Mitigation: Maintain heartbeat health checks and execute clean reconnection routines during unhandled disconnects.
  Owner: Integration Engineering Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Ensure all platform gateway dispatch routines operate within non-blocking asynchronous event loops to prevent stalling gateway heartbeats.
- Decouple internal transport schemas from platform-specific message embed presentations by translating payloads within bridge handlers.

## Continuation Context


Verify commands:
- Discover the project test runner and execute the integration test suite covering adapter gateway handlers and bridge dispatchers.
- Discover and run the architectural boundary linter to verify that direct platform client imports remain isolated within the adapter module hierarchy.

Accept when:
- All adapter integration tests pass without unhandled gateway connection exceptions.
- Architecture verification confirms platform client imports remain confined to the adapter package boundary.

## Enforcement

- Verified by: Automated architectural boundary linting in continuous integration pipelines.
- Verified by: Pull request review by integration engineering teams.
- Violation handling: Build failures triggered on direct chat client imports outside designated adapter packages.
- Violation handling: Rejection of pull requests attempting synchronous cross-boundary platform invocations.
- Exception process: Submit an architectural review request detailing technical constraints preventing adapter isolation.
- Exception process: Obtain approval from the lead integration architect prior to merging bypass logic.