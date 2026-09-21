# Precompiled Regular Expression Pattern Matching with the re Module: Before Implementing Updating Pattern Matching Logic

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Message adapters require real-time validation of incoming chat text to enforce channel content constraints including character set restrictions.
- Data processing utilities require deterministic extraction and masking of sensitive credentials, authentication tokens, and numeric platform identifiers prior to persistence or export.
- Repeated evaluation of complex pattern matching against streaming events and batch datasets demands precompiled pattern objects to minimize runtime parsing overhead.

## Problem Statement

Unstructured text ingestion in event adapters and data sanitization routines requires predictable pattern evaluation to enforce character restrictions and mask sensitive credentials. Dynamic pattern evaluation and fragmented parsing implementations introduce redundant parsing overhead during streaming event loops and increase the risk of inconsistent data sanitization across utilities.

## Decision

1. MUST: Before implementing or updating pattern matching logic that interfaces with versioned runtime libraries, consumers MUST inspect the repository lock or resolution artifact to determine the exact resolved version in accordance with the discovery policy.

## Policy Block

- MUST Before implementing or updating pattern matching logic that interfaces with versioned runtime libraries, consumers MUST inspect the repository lock or resolution artifact to determine the exact resolved version in accordance with the discovery policy.

In scope:
- Event adapter components performing character validation, content filtering, or message moderation.
- Administrative scripts and utilities executing identifier redaction, token masking, or text sanitization.

Out of scope:
- Simple exact string equality or prefix checks where standard string comparisons suffice without pattern parsing.
- Structured object deserialization and schema validation handled by typed parser components.

Exceptions:
- EXC-20-001: One-off exploratory tasks where execution occurs exactly once and patterns are not reused across iterations.

## Rationale

- Precompiling pattern objects via re.compile eliminates repetitive pattern interpretation costs during high-frequency message processing.
- Standardizing on compiled regular expression objects establishes consistent match and capture semantics across message adapters and data sanitization utilities.
- Utilizing the core re module satisfies character validation and credential masking requirements without introducing external parsing dependencies.

## Consequences

Positive:
- Uniform validation and sanitization semantics across message moderation handlers and data processing scripts.
- Elimination of repetitive pattern compilation overhead during high-frequency message event processing.
- Standardized masking and isolation of sensitive authentication tokens and entity identifiers without third-party dependencies.

Negative:
- Complex regular expression syntax introduces maintenance overhead and requires comprehensive unit test coverage to prevent regressions.
- Improperly structured regular expression patterns risk catastrophic backtracking under adversarial or malformed inputs.

## Alternatives

- Ad-hoc dynamic regular expression evaluation using module-level functions on each invocation (rejected)
  Rejected because: Re-parsing pattern strings during high-frequency event cycles incurs repeated compilation overhead and disperses validation logic across call sites.
  When valid: Single-execution scripts where performance overhead is negligible and patterns are evaluated exactly once.
- Adopting dedicated third-party parsing and tokenization libraries (rejected)
  Rejected because: Introduces external dependency management overhead when standard library pattern compilation fulfills all character range filtering and token masking requirements.
  When valid: Complex grammar parsing requirements necessitating abstract syntax tree construction or context-free grammar evaluation.

## Risks

- Catastrophic backtracking in regular expressions causing event loop starvation under adversarial inputs.
  Mitigation: Enforce explicit boundary anchors, avoid nested repetition operators, and validate expressions against performance test suites.
  Owner: Engineering Team
- Incomplete character range definitions leading to false positive rejections or unmasked credentials.
  Mitigation: Maintain centralized pattern definitions accompanied by comprehensive unit test cases covering character intervals and token formats.
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
- Instantiate precompiled regular expression objects at module or class scope during initialization rather than inside event loop handlers or per-message callbacks.
- Utilize anchored boundaries when defining identifier patterns to prevent unintended partial substring replacements during sanitization.

## Continuation Context


Verify commands:
- Discover the project test runner through the repository manifest configuration and execute test suites targeting moderation adapters and redaction utilities.
- Discover and execute the repository static analysis tooling to verify that regular expression operations do not execute dynamic uncompiled pattern calls in event loops.

Accept when:
- All pattern matching operations in event adapters and redaction utilities utilize precompiled regular expression objects instantiated at initialization scope.
- Automated test suites covering message content filtering and sensitive identifier redaction pass without regressions.
- Pattern matching verification confirms that non-conforming message payloads and sensitive credentials are accurately identified without catastrophic backtracking.

## Enforcement

- Verified by: Automated static analysis checks in continuous integration pipelines detecting uncompiled pattern evaluations in event handlers.
- Verified by: Peer code reviews verifying proper pattern scoping, boundary anchoring, and accompanying test coverage.
- Violation handling: Pull requests containing uncompiled pattern evaluations within event processing or data sanitization loops will be blocked from merging until refactored to precompiled objects.
- Exception process: Submit an exception proposal to the architecture review team documenting why precompilation or standard regular expression pattern matching is technically unfeasible.