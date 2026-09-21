# Discord Library Adoption for Bot Adapter Architecture: Interactive Discord Components Extend View Register

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- The application requires a robust integration adapter to handle Discord platform events, slash commands, interactive user components, and periodic background notifications.
- Multiple independent adapter modules require coordination with the Discord Gateway while maintaining clean architectural boundaries from core domain services.
- Static analysis detects widespread use of the discord library and its asynchronous component primitives across thirteen modules within the Discord adapter subsystem.

## Problem Statement

Integrating Discord platform capabilities such as slash commands, interactive UI components, message moderation, and scheduled reminders requires a consistent, event-driven framework that handles Gateway connection lifecycles without coupling core domain logic to external platform specifics.

## Decision

1. MUST: Interactive Discord UI components MUST extend discord.ui.View and register callback handlers via standard interaction callback methods.

## Policy Block

- MUST Interactive Discord UI components MUST extend discord.ui.View and register callback handlers via standard interaction callback methods.

In scope:
- All modules, command handlers, UI views, moderation enforcers, and tasks within the Discord adapter subsystem.
- All inbound and outbound communication interfaces interacting directly with the Discord Gateway or REST API.

Out of scope:
- Core domain logic, entities, services, and persistence layers located outside the Discord adapter subsystem.
- Adapters interfacing with non-Discord communication channels or generic third-party external services.

## Rationale

- Adopting the discord library provides established asynchronous protocol handling, interactive UI primitives, and gateway lifecycle management across all thirteen observed adapter modules.
- Standardizing on discord.ui components and interaction response mechanisms ensures consistent user experience and predictable ephemeral error handling across command handlers.
- Encapsulating discord library dependencies within adapter packages prevents external platform coupling from spreading into internal event and domain logic.

## Consequences

Positive:
- Standardizes interactive UI presentation through structured views, select menus, and modal forms across Discord commands.
- Eliminates custom WebSocket gateway protocol maintenance and provides native lifecycle-aligned background task execution.
- Encapsulates Discord platform integration logic within a dedicated adapter boundary, insulating internal domain logic from third-party API churn.

Negative:
- Introduces architectural coupling to discord library API contracts and asynchronous runtime conventions within the adapter layer.
- Requires asynchronous concurrency and event-driven patterns across all command handling, view callbacks, and scheduled tasks.

## Alternatives

- Direct Discord Gateway WebSocket and REST HTTP client implementation (rejected)
  Rejected because: Building and maintaining custom Gateway heartbeats, rate limiting, and interaction payload deserialization creates substantial maintenance overhead and duplicates existing library capabilities.
  When valid: Valid only when building an ultra-minimal standalone webhook receiver that requires zero interactive UI or gateway event listening.
- Multi-platform generic bot abstraction framework (rejected)
  Rejected because: Generic chat platform abstractions impose lowest-common-denominator interfaces that restrict Discord-specific features including custom UI views, modals, and ephemeral interaction responses.
  When valid: Valid when the application must simultaneously support identical conversational interaction models across multiple distinct messaging networks.

## Risks

- Upstream breaking changes in discord library releases altering interaction payloads or UI component lifecycles.
  Mitigation: Pin exact dependency versions in repository lock files and isolate discord library types inside the adapter module boundary.
  Owner: Engineering Team
- Leaking Discord platform-specific types and interaction contracts into business domain services.
  Mitigation: Enforce strict module boundaries via automated static analysis and translate Discord interaction payloads into internal domain DTOs within adapter handlers.
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
- Implement interactive user interface components by subclassing the standard view class and dispatching user input through dedicated modal and select callback handlers.
- Coordinate Discord client lifecycle events and guild registration state through the central bot manager instance inside the adapter subsystem.

## Continuation Context


Verify commands:
- Discover and run the project static analysis verification to ensure discord imports remain restricted to the adapter boundary.
- Discover and run the repository test suite to validate command handlers, UI view callbacks, and scheduled tasks.

Accept when:
- Static analysis confirms all Discord interactions, UI views, and background tasks conform to discord library contracts within the adapter layer.
- Test suite passes all unit and integration specifications for command handling, UI modal interactions, and background task loops without leaking platform types across subsystem boundaries.

## Enforcement

- Verified by: Automated static analysis verifying module import boundaries and prohibiting discord library imports outside the adapter package.
- Verified by: Continuous integration test suites verifying command handlers, modal submissions, and background task execution.
- Verified by: Peer code reviews verifying compliance with UI view inheritance and interaction response conventions.
- Violation handling: Continuous integration failure upon detection of unauthorized external imports of discord library symbols.
- Violation handling: Pull request rejection for interaction handlers failing to satisfy ephemeral messaging and view encapsulation requirements.
- Exception process: Submit an architecture exception request detailing why the standard discord library constructs or adapter boundaries cannot satisfy the functional requirement.
- Exception process: Obtain formal review and written sign-off from principal engineering leads prior to merging non-standard communication patterns.