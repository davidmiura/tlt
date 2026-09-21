# discord Library UI Modal and Interaction Handler Adoption: Submit Callback Discord Modal Delegate Input

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- The platform adapter interface requires capturing structured user input for event creation and event lifecycle operations.
- Interactive user interface dialogs in the platform adapter require clean separation between platform-specific UI lifecycles and business execution handlers.
- Asynchronous modal callbacks must delegate submission payloads consistently across interactive command interfaces and event bridge components.

## Problem Statement

Interactive platform commands requiring multi-field user input risk coupling presentation-layer modal dialog lifecycles directly to event processing and backend execution logic, reducing reusability and hindering testability across adapter boundaries.

## Decision

1. MUST: The on_submit callback of a discord.ui.Modal MUST delegate input processing to a dedicated handler instance via an asynchronous handle_modal_submission invocation passing the interaction context and field values.

## Policy Block

- MUST The on_submit callback of a discord.ui.Modal MUST delegate input processing to a dedicated handler instance via an asynchronous handle_modal_submission invocation passing the interaction context and field values.

In scope:
- Interactive user input collection forms within platform adapter command modules.
- Event bridge handlers processing structured modal submission interactions.

Out of scope:
- Direct text-based slash commands that do not present modal user interface forms.
- Core business domain services operating outside the platform adapter boundary.

## Rationale

- Subclassing discord.ui.Modal with declarative discord.ui.TextInput components provides platform-native structured input capture with built-in length and requirement validation.
- Delegating modal submission processing to dedicated handler classes decouples the presentation lifecycle from event orchestration and external service interactions.
- Consistent handler delegation enables both interactive UI forms and event bridge consumers to share unified submission logic.

## Consequences

Positive:
- Enforces clean architectural boundary between discord presentation UI components and business domain logic.
- Enables reusable modal submission handling across distinct integration entrypoints and bridge event pipelines.
- Facilitates isolated unit testing of event creation and update handling without instantiating platform UI widgets.

Negative:
- Requires additional handler abstractions and indirection for simple modal interactions.
- Requires careful synchronization between modal field declarations and handler parameter signatures.
- Requires strict lifecycle management for bot instance references passed to modal components and handlers.

## Alternatives

- In-line modal submission handling within modal callback methods (rejected)
  Rejected because: Couples UI component lifecycle and presentation structures directly to business processing logic and external adapter communications.
  When valid: Valid only in trivial single-purpose prototypes where event handling involves no asynchronous external coordination.
- Unstructured conversational text prompts for event data collection (rejected)
  Rejected because: Requires complex conversational state machines and unstructured input parsing that increases validation errors.
  When valid: Valid in conversational environments where structured interactive modal dialogs are unsupported by the platform.

## Risks

- Interaction token timeout if handler processing exceeds platform modal response deadlines.
  Mitigation: Ensure modal callbacks invoke handlers asynchronously and provide timely user interaction feedback before platform interaction tokens expire.
  Owner: engineering team
- Stale or uninitialized bot instance references passed into modal handlers.
  Mitigation: Pass bot runtime dependencies explicitly into modal initializers or handlers without coupling to global state.
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
- Instantiate submission handlers with necessary runtime bot instances during modal submission callbacks rather than retaining long-lived cyclic references in UI components.
- Maintain typed input field value extraction at the modal boundary before dispatching clean primitive or domain arguments to the handling layer.

## Continuation Context


Verify commands:
- Discover the repository dependency verification command and run it to verify that installed library versions match the authoritative lock artifact.
- Discover the repository test runner script and execute unit tests covering adapter modal classes and submission handlers.
- Discover the repository static analysis linter and run it against adapter command and event bridge packages to confirm handler delegation compliance.

Accept when:
- All modal user input interactions subclass the discord UI modal base class and delegate submission payloads to dedicated interaction handlers.
- Static analysis and test suites verify that modal callback methods contain no direct persistence or business domain logic.
- The project dependency lock artifact is inspected and verified prior to consuming discord UI component APIs.

## Enforcement

- Verified by: Automated static analysis rules and code linters verifying handler delegation within modal callbacks.
- Verified by: Continuous integration automated test suite validating modal submission and handler dispatch workflows.
- Verified by: Peer code review required for all adapter interface command and event bridge pull requests.
- Violation handling: Pull requests with business domain logic located inside modal UI classes will be blocked during automated review.
- Violation handling: Violations discovered in main branches require immediate refactoring into dedicated interaction handlers.
- Exception process: Exceptions must be submitted via architectural change request detailing why modal submission logic cannot be delegated to an independent handler.
- Exception process: Approval requires sign-off from adapter architecture maintainers prior to merging non-delegated modal logic.