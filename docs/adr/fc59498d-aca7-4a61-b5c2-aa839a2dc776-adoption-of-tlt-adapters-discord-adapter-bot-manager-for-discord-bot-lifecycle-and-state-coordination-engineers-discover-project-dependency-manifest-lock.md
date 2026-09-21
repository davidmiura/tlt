# Adoption of tlt.adapters.discord_adapter.bot_manager for Discord Bot Lifecycle and State Coordination: Engineers Discover Project Dependency Manifest Lock

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- The Discord adapter subsystem comprises multiple discrete interaction handlers including slash commands, modal submissions, interactive UI select menus, automated message moderation enforcers, and health monitoring endpoints.
- Operating a Discord integration requires consistent gateway connection lifecycle handling, guild registration tracking, authorization verification, and in-memory event state synchronization across concurrent asynchronous interactions.
- Decentralized gateway management or autonomous state tracking across individual command handlers risks gateway connection exhaustion, inconsistent permission enforcement, and split-brain event states across interactions.

## Problem Statement

Decentralized interaction handling across numerous command handlers, UI views, and event listeners leads to fragmented gateway connections, duplicated authorization logic, and inconsistent in-memory state tracking. The Discord adapter requires an authoritative architectural mechanism to coordinate bot lifecycle, manage active event registries, verify administrative permissions, and report connection readiness without scattering gateway dependencies.

## Decision

1. MUST: Engineers MUST discover the project dependency manifest and lock artifact to resolve the exact locked version of all underlying platform libraries and runtime dependencies before implementation, verifying that all invoked interfaces conform to version-specific documentation.

## Policy Block

- MUST Engineers MUST discover the project dependency manifest and lock artifact to resolve the exact locked version of all underlying platform libraries and runtime dependencies before implementation, verifying that all invoked interfaces conform to version-specific documentation.

In scope:
- All command handlers, UI views, event bridges, moderation enforcers, and operational endpoints within the Discord adapter package.
- Any interaction handling Discord guild registration, permissions, event state, or gateway readiness.

Out of scope:
- Core business logic services located outside the Discord adapter boundary.
- Stateless utility functions with no platform or lifecycle dependencies.

## Rationale

- Consolidating bot lifecycle and runtime state within tlt.adapters.discord_adapter.bot_manager ensures a single authoritative gateway connection and unified active event registry across all thirteen observed adapter submodules.
- Centralizing administrative verification via the is_admin contract eliminates divergent permission checks across command handlers and interactive views.
- Providing dependency injection of the bot manager into views and modal handlers ensures interaction flows retain state continuity without resorting to global singleton mutation.

## Consequences

Positive:
- Ensures unified gateway connection lifecycle and centralized ready status reporting across operational and monitoring endpoints.
- Standardizes permission enforcement and guild registration checks across all interactive slash commands and UI components.
- Prevents state drift by maintaining an authoritative active events and guild settings registry within a single manager.

Negative:
- Creates direct coupling between all adapter subcomponents and the bot manager module interface.
- In-memory state management in the bot manager introduces synchronization bottlenecks if the adapter scales horizontally across multiple processes.
- Handler unit testing requires mocking or stubbing the bot manager interface across all command and view test suites.

## Alternatives

- Autonomous gateway client instances per command module (rejected)
  Rejected because: Creating independent gateway client connections within individual command handlers exhausts connection limits and prevents unified event state sharing.
  When valid: Only viable in lightweight serverless environments where stateless ephemeral webhooks replace persistent gateway connections.
- Direct external datastore persistence without an in-memory manager (rejected)
  Rejected because: Eliminating the internal bot manager increases database I/O latency for frequent interaction lookups and requires complex pub-sub mechanisms for gateway readiness synchronization.
  When valid: Viable when horizontal multi-process clustering requires distributed cache synchronization across multiple container replicas.

## Risks

- Failure or unhandled exception within the central bot manager disrupts all command handling and health reporting.
  Mitigation: Isolate individual interaction handler execution within structured try-except blocks and provide defensive fallback responses to user interactions.
  Owner: engineering team
- Memory accumulation in active events and guild settings dictionaries over prolonged uptime.
  Mitigation: Implement periodic cleanup routines and lifecycle callbacks upon guild removal or event deletion.
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
- Construct handlers and views with explicit bot manager injection rather than relying on module-level global lookups where possible.
- Validate that all command responses handle ephemeral interaction expirations gracefully during downstream processing.

## Continuation Context


Verify commands:
- Discover and run the project test suite to verify adapter command and view integration against the bot manager.
- Discover and execute the repository static analysis tooling to verify all adapter modules conform to bot manager contract signatures.

Accept when:
- All adapter command handlers, views, and event enforcers successfully route lifecycle, permission, and state calls through the bot manager interface without runtime exceptions.
- Verification test suites pass with zero unregistered guild bypasses and consistent permission validation.

## Enforcement

- Verified by: Continuous integration test suites validating command, view, and moderation interactions against mock bot manager instances.
- Verified by: Peer code review verifying that new adapter handlers consume the bot manager rather than instantiating external platform clients.
- Violation handling: Pull requests introducing uncoordinated platform client instantiations or bypassing bot manager state checks MUST be blocked by automated checks and review gates.
- Violation handling: Architectural violations must be remediated by refactoring handlers to accept and query the central bot manager instance.
- Exception process: Exceptions for standalone administrative utilities or stateless webhooks require written architectural review and sign-off documenting alternate state handling.