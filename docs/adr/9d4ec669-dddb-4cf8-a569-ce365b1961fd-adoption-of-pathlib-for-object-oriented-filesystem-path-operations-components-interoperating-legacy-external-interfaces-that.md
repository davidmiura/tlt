---
version: 2
name: 9d4ec669-dddb-4cf8-a569-ce365b1961fd-adoption-of-pathlib-for-object-oriented-filesystem-path-operations-components-interoperating-legacy-external-interfaces-that
description: "Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Interoperating Legacy External Interfaces That"
metadata:
  actual:
    adr_id: 9d4ec669-dddb-4cf8-a569-ce365b1961fd
    status: accepted
    candidate_group_id: c5305f67-e193-43d8-a4de-d0abb9bfaee8
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Adoption of pathlib for Object-Oriented Filesystem Path Operations: Components Interoperating Legacy External Interfaces That

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/mcp_services/**`
- `tlt/services/tlt_service/**`
- `tlt/shared/**`

## Context

- Services and shared modules across the codebase require consistent filesystem operations for configuration discovery, state persistence roots, and localized resource resolution.
- Legacy string manipulation approaches for filesystem paths introduce cross-platform fragility and verbose nesting of directory operations.
- The codebase demonstrates adoption of the pathlib module to provide structured, object-oriented path abstractions and clean path compositions across service components and shared state managers.
- Inconsistent path resolution between string-based manipulations and structured path objects creates maintenance overhead and increases the risk of path traversal errors.

## Problem Statement

Services and state persistence modules require a dependable, standardized mechanism for resolving filesystem paths to configuration files, resource directories, and storage roots. Relying on string-based path concatenation and nested directory navigation functions creates brittle, platform-dependent code that is difficult to maintain and prone to subtle path resolution errors.

## Decision

1. MAY: Components interoperating with legacy external interfaces that strictly demand primitive string paths MAY convert Path instances using string coercion at the immediate interface boundary.

## Policy Block

- MAY Components interoperating with legacy external interfaces that strictly demand primitive string paths MAY convert Path instances using string coercion at the immediate interface boundary.

In scope:
- All backend services, microservice endpoints, and shared state management modules performing filesystem operations, configuration loading, or local persistence.

Out of scope:
- Pure in-memory operations and cloud-native object storage operations that do not interact with local or mounted filesystem abstractions.

Exceptions:
- EXC-20-001: Interacting with external third-party SDKs that strictly enforce string type validation on file arguments without accepting Path objects

## Rationale

- Object-oriented path representations encapsulate path operations within immutable, semantically rich objects, reducing bugs related to platform path separators.
- Utilizing pathlib standardizes path composition across services and shared persistence layers, replacing verbose nested directory calls with intuitive path operators.
- Establishing a single path manipulation paradigm simplifies static analysis, improves readability, and avoids split-brain filesystem logic where string paths and path objects are mixed.

## Consequences

Positive:
- Standardizes cross-platform path handling across differing operating system filesystem conventions.
- Improves maintainability by replacing nested directory extraction calls with clean operator-based path composition.
- Provides structured path validation for configuration discovery and state persistence roots.

Negative:
- Requires explicit string type coercion when interfacing with third-party libraries that do not accept path objects.
- Demands migration effort to eliminate legacy string-based path manipulations across existing service modules.

## Alternatives

- Continue using legacy string-based path manipulation functions and string concatenation (rejected)
  Rejected because: Results in verbose nested function calls, lacks object-oriented encapsulation, and creates error-prone path separator concatenation defects.
  When valid: When maintaining legacy scripts in environments restricted to legacy interpreters without modern standard library access.
- Introduce a custom first-party filesystem path wrapper abstraction (rejected)
  Rejected because: Imposes unnecessary maintenance overhead when the standard library module already provides comprehensive path manipulation capabilities.
  When valid: When specialized virtual filesystem abstractions or remote file streaming semantics must be unified under a proprietary interface.

## Risks

- Passing Path objects into legacy APIs that expect primitive string types may cause runtime type errors.
  Mitigation: Coerce Path objects to string representations at external boundaries and enforce type annotations across interface contracts.
  Owner: Core Engineering Team
- Inconsistent adoption where both string-based and object-oriented path utilities co-exist within the same service codebase.
  Mitigation: Add static analysis rules to flag legacy path operations in pull requests and continuous integration checks.
  Owner: Architecture Review Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Anchor path discovery to the execution module location by instantiating Path from the module identity and resolving the parent directory hierarchy.
- Perform all path concatenations and child resolutions using the slash operator before evaluating path existence or reading filesystem contents.

## Continuation Context


Verify commands:
- Discover the project static analysis and linting command from the repository configuration and execute it to verify absence of string-based path manipulation functions.
- Discover the automated test runner command from the repository configuration and run the test suite to verify that path resolution operates correctly across all target environments.

Accept when:
- Static analysis reports zero occurrences of disallowed string-based path manipulation functions in service and shared modules.
- All automated integration and unit test suites pass without filesystem path resolution errors across supported runtime environments.

## Enforcement

- Verified by: Static analysis checks configured in the automated integration pipeline.
- Verified by: Peer code review verification during pull request reviews.
- Violation handling: Automated continuous integration pipeline failure blocking code merges.
- Violation handling: Requirement to refactor non-compliant path manipulation logic to use Path objects before branch approval.
- Exception process: Formal architectural exception request submitted with technical justification where external constraints prevent direct path object usage.