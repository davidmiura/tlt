---
version: 2
name: 6c73468b-b825-43de-8f86-99178e70c666-re-module-for-precompiled-pattern-validation-and-credential-redaction-text-validation-character-moderation-sensitive-token
description: "re Module for Precompiled Pattern Validation and Credential Redaction: Text Validation Character Moderation Sensitive Token"
metadata:
  actual:
    adr_id: 6c73468b-b825-43de-8f86-99178e70c666
    status: accepted
    candidate_group_id: 7812eaa4-5196-4b53-91a2-64db19f1be66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/scripts/**
---

# re Module for Precompiled Pattern Validation and Credential Redaction: Text Validation Character Moderation Sensitive Token

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/scripts/**`

## Context

- The platform ingests dynamic event interactions from external chat adapters that require deterministic character moderation to enforce thread communication constraints.
- Administrative export utilities and image extraction pipelines process payloads containing sensitive platform authentication tokens, secret keys, and entity identifiers that must be sanitized prior to storage or display.
- High-frequency event loops and batch processing routines require zero-dependency, in-memory pattern matching to avoid introducing network latency into core workflows.

## Problem Statement

External adapter events and administrative export workflows require consistent content validation and credential sanitization. Uncontrolled string manipulation or dynamic pattern evaluation introduces latency, inconsistent masking of sensitive keys, and risk of catastrophic backtracking during message processing.

## Decision

1. MUST: All text validation, character moderation, and sensitive token redaction across adapter interfaces and batch utilities MUST use precompiled patterns created via the re module rather than runtime inline pattern parsing or ad-hoc string slicing.

## Policy Block

- MUST All text validation, character moderation, and sensitive token redaction across adapter interfaces and batch utilities MUST use precompiled patterns created via the re module rather than runtime inline pattern parsing or ad-hoc string slicing.

In scope:
- Inbound message content filtering and character moderation in communication adapters.
- Batch data sanitization, image text redaction pipelines, and export data scrubbers requiring detection of authentication tokens, secret keys, and platform identifiers.

Out of scope:
- Complex natural language understanding, entity extraction, or conversational semantic analysis requiring dedicated parsing models.
- Structured data schema validation or persistence boundary constraints handled by primary data modeling libraries.

Exceptions:
- EXC-20-001: A string inspection operation requires single constant substring matching that can be evaluated via exact equality without pattern evaluation.

## Rationale

- Precompiling regular expression definitions via the re module provides deterministic execution performance and eliminates repeated compilation overhead across high-frequency adapter events.
- Standardizing pattern definitions for sensitive tokens and content validation ensures unified redaction behavior across both real-time adapters and asynchronous batch export scripts.
- Utilizing the standard regular expression module avoids introducing external network dependencies or heavyweight parsing frameworks for lexical filtering and redaction tasks.

## Consequences

Positive:
- Eliminates external network latency and third-party availability dependencies for inline message moderation and sensitive data masking.
- Ensures consistent redaction behavior across both live adapter messaging paths and asynchronous administrative data pipelines.
- Minimizes runtime execution overhead by compiling static patterns once at module initialization.

Negative:
- Regular expression patterns remain vulnerable to maintainability degradation as credential formats and unicode ranges change.
- Risk of resource exhaustion or latency spikes if pattern alterations introduce unmitigated catastrophic backtracking paths.
- Complex unicode character filtering may fail to cover novel composite emoji sequences without continuous pattern maintenance.

## Alternatives

- External Content Moderation and Data Loss Prevention Service (rejected)
  Rejected because: Network round-trip latency and external service rate limits are incompatible with synchronous event processing loops and offline administrative batch scripts.
  When valid: Valid when multi-modal intent detection or contextual semantic analysis across natural language is explicitly required.
- Ad-hoc Substring Slicing and Dynamic Split Parsing (rejected)
  Rejected because: Lacks boundary validation and delimiter enforcement, introducing parsing fragility and risking partial leakage of sensitive authentication keys.
  When valid: Valid only for fixed-format, static strings where structural pattern variance is impossible.

## Risks

- Catastrophic backtracking triggered by maliciously crafted inputs matching ambiguous pattern structures.
  Mitigation: Enforce pattern review standards, disallow nested open quantifiers, and test expressions against worst-case input payloads.
  Owner: Platform Engineering
- Pattern obsolescence due to upstream provider token format modifications leading to unredacted credential leaks.
  Mitigation: Maintain automated test fixtures validating pattern matches against current provider credential specifications.
  Owner: Data Engineering

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Define all precompiled regular expression pattern constants at module scope to guarantee single initialization upon initial load.
- When defining character ranges for character-class validation, specify boundary code points explicitly and avoid unanchored pattern matches.

## Continuation Context


Verify commands:
- test -n "$REPOSITORY_TEST_SUITE" && $REPOSITORY_TEST_SUITE || echo "Execute test suite discovered from repository manifest"
- test -n "$REPOSITORY_LINTER" && $REPOSITORY_LINTER || echo "Execute linting suite discovered from repository manifest"

Accept when:
- All unit and integration tests validating pattern matching and redaction utilities pass successfully without errors.
- Zero unanchored dynamic regular expression compilations exist within message handling loops or batch iteration paths.

## Enforcement

- Verified by: Automated test suites executing pattern verification fixtures in continuous integration pipelines.
- Verified by: Peer code review confirming adherence to module-level precompilation standards and absence of catastrophic backtracking vulnerabilities.
- Violation handling: Pull requests containing inline pattern recompilation inside loops or unanchored regular expressions are blocked until remediated.
- Exception process: Submit an architectural deviation proposal documenting performance benchmarks or specific parsing constraints to the platform engineering lead for review.