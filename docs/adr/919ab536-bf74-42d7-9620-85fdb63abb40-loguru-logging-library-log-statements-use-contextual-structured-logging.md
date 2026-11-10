---
version: 2
name: 919ab536-bf74-42d7-9620-85fdb63abb40-loguru-logging-library-log-statements-use-contextual-structured-logging
description: "Loguru Logging Library: Log Statements Use Contextual Structured Logging"
metadata:
  actual:
    adr_id: 919ab536-bf74-42d7-9620-85fdb63abb40
    status: accepted
    candidate_group_id: 8a266a3f-c7bf-4e9e-8fc9-2346e2c48d8f
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/**
---

# Loguru Logging Library: Log Statements Use Contextual Structured Logging

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/mcp_services/**`

## Context

- Service modules require consistent, low-ceremony diagnostic and operational logging across distributed service workflows.
- The codebase establishes direct imports of logger from loguru across multiple service components, avoiding manual logging handler configuration.
- A single logging framework is necessary to ensure consistent output formatting and structured log capture across services.

## Problem Statement

Disparate logging mechanisms across backend services create maintenance friction and complicate centralized log aggregation. Without a standardized logging library adoption, individual components risk implementing divergent logging wrappers, inconsistent level thresholds, or ad-hoc formatting conventions.

## Decision

1. SHOULD: Log statements SHOULD use contextual structured logging capabilities, including parameterized message strings and exception trace formatting, when emitting error states.

## Policy Block

- SHOULD Log statements SHOULD use contextual structured logging capabilities, including parameterized message strings and exception trace formatting, when emitting error states.

In scope:
- Service modules, background processing workflows, and tool handlers requiring operational or diagnostic telemetry.

Out of scope:
- Standalone utility scripts and external interface schemas that do not emit runtime logs.

Exceptions:
- EXC-20-001: Third-party framework boundaries require passing a standard library logging interface.

## Rationale

- Evidence across service implementations demonstrates uniform direct import of logger from loguru, indicating an established convention across multiple services.
- Adopting Loguru provides out-of-the-box structured logging and consistent exception formatting without requiring repetitive logger instantiation boilerplate.
- Standardizing on a single library simplifies logging maintenance and unifies log output parsing across service boundaries.

## Consequences

Positive:
- Establishes consistent log message format and call conventions across all participating service modules.
- Eliminates repetitive logger configuration boilerplate across distributed service files.
- Simplifies error capture and stack trace formatting across processing pipelines.

Negative:
- Couples service implementations to an external third-party logging library.
- Potential integration friction when interoperating with external dependencies that expect standard library logging handlers.

## Alternatives

- Standard library logging module (rejected)
  Rejected because: Requires explicit handler configuration, formatter setup, and boilerplate instantiation across each module.
  When valid: In minimal dependency environments where zero third-party packages are permitted.
- Custom in-house logging abstraction wrapper (rejected)
  Rejected because: Introduces internal maintenance burden without providing functional advantages over the adopted library.
  When valid: When proprietary telemetry protocols dictate custom transport layers.

## Risks

- Incompatible API changes across major version updates of the external logging library.
  Mitigation: Strictly enforce lock-version grounding by checking project lock artifacts before updating dependency references.
  Owner: engineering team
- Unsynchronized log handler configurations across independently executing service modules.
  Mitigation: Centralize root sink configurations at service startup routines.
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
- Import logger from the adopted library at the module top level and use contextual logging methods for error handling and event tracing.
- Configure global sinks and log levels during application initialization prior to executing background workflows.

## Continuation Context


Verify commands:
- Discover the project's static analysis script in the workspace configuration and execute it to verify logging imports conform to the standard.
- Discover the project's test runner script from the repository manifest and execute the test suite to verify log emission behavior.

Accept when:
- All service modules import logger from loguru without introducing alternate logging frameworks or standard library logger boilerplate.
- Automated static analysis and test validation suites pass without logging-related lint or runtime errors.

## Enforcement

- Verified by: Automated static analysis checks in continuous integration pipelines.
- Verified by: Peer code reviews for new and modified service modules.
- Violation handling: Pull requests introducing direct standard library logging instantiation or alternative logging frameworks will be blocked until updated.
- Exception process: Submit an architectural exception request detailing interoperability constraints with third-party logging sinks for review by the architecture team.