# Discord Interaction Handling via Ephemeral Response Messaging: Integration Error Responses Generated During Command

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Chat platform integration adapters process command invocations and UI interactions that require immediate acknowledgement and contextual feedback.
- Broadcasting administrative notices, validation errors, and selection menus to public channels creates noise and exposes operational state to unauthorized members.
- The discord integration library provides interaction response primitives enabling direct, private feedback delivery scoped to the invoking user.
- Consistent interaction handling across adapter command modules prevents unhandled interaction timeouts and standardizes authorization verification.

## Problem Statement

When integrating external chat platform commands with backend services, command handlers must provide prompt, private, and secure feedback for validation, permissions, and status updates without polluting public chat channels or exceeding interaction response timeouts. Without a standardized interaction response convention, handlers risk channel clutter, information leakage, and unhandled interaction failures across adapter command implementations.

## Decision

1. MUST_NOT: Integration error responses generated during command handling MUST NOT expose raw internal exceptions or sensitive server metadata to interaction responses.

## Policy Block

- MUST_NOT Integration error responses generated during command handling MUST NOT expose raw internal exceptions or sensitive server metadata to interaction responses.

In scope:
- Discord adapter command handlers and interaction callbacks processing incoming guild and user events.
- User interface views and modals handling interaction events within the chat adapter boundary.

Out of scope:
- Public broadcast notifications initiated asynchronously outside user interaction contexts.
- Internal service-to-service communication mechanisms decoupled from the chat adapter interface.

Exceptions:
- EXC-27-001: A command explicitly publishes a public guild announcement intended for all channel members rather than an individual invoking user.

## Rationale

- Utilizing interaction responses with ephemeral delivery ensures that sensitive validation errors, permission rejections, and intermediate state menus remain visible only to the initiating user.
- Direct acknowledgement within the platform interaction lifecycle prevents gateway timeout errors while isolating command orchestration from public chat streams.
- Enforcing standard response handling across adapter command modules maintains uniform authorization gates prior to backend service client dispatch.

## Consequences

Positive:
- Prevents public chat channel clutter by restricting administrative feedback and validation messages to the invoking user.
- Mitigates exposure of internal server identifiers and operational validation details to unauthorized channel members.
- Standardizes interaction lifecycle acknowledgement timing and authorization checks across all adapter command handlers.

Negative:
- Ephemeral interaction responses cannot be re-inspected by users once dismissed or audited by other channel members.
- Requires separate handling paths when a command workflow intentionally concludes with a public channel announcement.

## Alternatives

- Public Channel Response Messaging (rejected)
  Rejected because: Pollutes public conversation channels with user-specific validation notices, permission rejections, and intermediate state menus.
  When valid: Valid only when a command explicitly creates a persistent public announcement intended for all channel participants.
- Deferred Webhook Callback Processing (rejected)
  Rejected because: Introduces unnecessary asynchronous callback complexity and webhook coordination overhead for operations that complete within the initial interaction response window.
  When valid: Valid when backend integration operations exceed the synchronous interaction acknowledgement deadline.

## Risks

- Interaction gateway timeout expiration if backend client operations block prior to dispatching response.
  Mitigation: Acknowledge interactions immediately with ephemeral status messages or defer interactions prior to executing long-running operations.
  Owner: Integration Engineering Team
- Information loss when users dismiss ephemeral confirmation responses before completing multi-step actions.
  Mitigation: Present multi-step state mutations within modal interfaces and persist relevant event state in backend storage.
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
- Implement permission validation guards at the entry point of each interaction handler before invoking backend integration clients.
- Encapsulate interactive user confirmation workflows within dedicated modal components rather than multi-message channel exchanges.

## Continuation Context


Verify commands:
- Discover and execute the project test suite runner to validate adapter interaction handler compliance.
- Discover and execute the project static analysis and linting verification scripts to check interaction response configurations.

Accept when:
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

## Enforcement

- Verified by: Continuous integration test suites validating interaction handler response flags and exception handling.
- Verified by: Peer review verifying that all validation and permission checks route through ephemeral responses.
- Violation handling: Pull requests introducing non-ephemeral responses for validation, permission checks, or error paths will be blocked.
- Violation handling: Static analysis or test failures on unacknowledged interaction lifecycles must be resolved prior to merge.
- Exception process: Submit an architectural exception request documenting why public channel delivery is required for a specific command interaction.
- Exception process: Obtain approval from the integration architecture team before introducing non-ephemeral response flows.