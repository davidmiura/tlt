# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Developers Inspect Repository Dependency Resolution Artifact

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Executable components across the repository, including autonomous agents, configuration validation scripts, and data manipulation utilities, require structured command-line argument handling.
- Disparate argument parsing approaches create inconsistent invocation syntax, inadequate validation of operational parameters, and tightly coupled execution logic that resists automated testing.
- Standardizing on the argparse library module establishes a unified interface contract across agent runners and operational scripts while avoiding third-party dependency bloat.

## Problem Statement

Without a standardized command-line parsing library, executable scripts and agent entrypoints risk adopting divergent argument parsing techniques, ranging from fragile manual argument index inspection to redundant external dependencies. This divergence creates inconsistent developer workflows, brittle configuration loading, and difficult unit testing for entrypoint contracts.

## Decision

1. MUST: Developers MUST inspect the repository dependency resolution artifact to confirm the runtime environment baseline and ensure compatibility with the standard library module APIs prior to introducing new argument parsing interfaces.

## Policy Block

- MUST Developers MUST inspect the repository dependency resolution artifact to confirm the runtime environment baseline and ensure compatibility with the standard library module APIs prior to introducing new argument parsing interfaces.

In scope:
- Executable agent entrypoints and background service runners requiring command-line configuration
- Utility scripts, data processing workflows, and operational validation tools executed via command line

Out of scope:
- Internal domain services, pure computational modules, and helper libraries that do not expose an executable command-line interface
- Microservices that receive configuration exclusively through environment variables or centralized configuration providers without CLI flags

Exceptions:
- EXC-20-001: A complex multi-command CLI tool requires nested subcommands or interactive terminal UI features that exceed standard argparse capabilities

## Rationale

- Adopting argparse establishes a consistent, standard-library-backed interface for defining command-line contracts across all executable scripts and agent entrypoints.
- Extracting argument parsing into structured configuration functions separates CLI parameter handling from core execution lifecycles, enabling deterministic testing of configuration generation.
- Standardizing on the built-in argparse module eliminates the need for external CLI framework dependencies, minimizing dependency maintenance overhead and potential supply chain risks.

## Consequences

Positive:
- Consistent invocation patterns, automatic help documentation, and standardized parameter validation across all repository scripts and agent entrypoints.
- Zero external dependency footprint for command-line parsing, reducing dependency bloat and vulnerability attack surface.
- Improved testability by isolating parameter parsing logic into callable contract functions that generate typed configuration objects.

Negative:
- Requires boilerplate argument parser configuration compared to certain higher-level decorator-based third-party CLI frameworks.
- Nested command hierarchies and complex multi-level subcommands require manual parser scaffolding.

## Alternatives

- Manual parameter parsing using raw system argument vectors (rejected)
  Rejected because: Manual vector slicing lacks automated type casting, provides no standardized help documentation, and introduces fragile error handling
  When valid: Trivial one-off debugging snippets that will never be committed to the repository
- Third-party CLI frameworks with decorator-driven syntax (rejected)
  Rejected because: Introduces external runtime dependencies and transitive supply chain overhead for capabilities that standard library modules sufficiently satisfy
  When valid: Rich interactive command-line applications requiring advanced terminal styling, shell auto-completion, or progress bar management

## Risks

- Inconsistent argument naming conventions across different scripts creating cognitive friction for operators
  Mitigation: Establish standardized naming conventions for common operational flags such as debug modes, configuration paths, and timeout thresholds
  Owner: engineering team
- Coupling argument parsing directly to process termination or exit routines, hindering automated test coverage
  Mitigation: Mandate the separation of parser construction and argument transformation from runtime execution entrypoints
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
- Construct argument parsing logic inside isolated functions that accept an argument sequence parameter defaulting to system arguments, allowing test harnesses to supply custom argument arrays.
- Ensure all parser definitions specify explicit help strings and appropriate type conversions for numerical or structured parameters.

## Continuation Context


Verify commands:
- eval "$PROJECT_TEST_COMMAND"
- eval "$PROJECT_LINT_COMMAND"

Accept when:
- All unit tests exercising command-line argument parsing and configuration creation pass successfully without errors.
- Static analysis and lint checks verify that all executable entrypoints adhere to standardized argument parser contracts.

## Enforcement

- Verified by: Automated continuous integration test suites verifying argument parsing contracts
- Verified by: Peer code review for all new and modified script and agent entrypoint implementations
- Violation handling: Pull requests containing ad-hoc argument parsing or unapproved third-party CLI libraries are blocked until corrected to follow the standard pattern
- Exception process: Exceptions must be submitted via an architecture decision proposal detailing why standard argument parsing is insufficient, subject to lead engineer sign-off