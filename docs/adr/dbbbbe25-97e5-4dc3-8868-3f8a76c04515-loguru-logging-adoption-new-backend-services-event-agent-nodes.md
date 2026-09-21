# Loguru Logging Adoption: New Backend Services Event Agent Nodes

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Asynchronous event handling pipelines and distributed microservices require consistent, informative diagnostic telemetry across concurrent task execution nodes.
- Multiple service modules, protocol gateways, and event agent execution nodes have adopted the Loguru logging library directly rather than relying on standard library logging initialization.
- Standardizing logging mechanics ensures uniform diagnostic output, predictable exception formatting, and consistent context tracking across services.

## Problem Statement

Asynchronous event agent workflows and multi-service systems suffer from inconsistent telemetry and diagnostic visibility when logging patterns vary across modules, necessitating a standardized logging interface that provides structured output and unified operational tracing without repetitive boilerplate configuration.

## Decision

1. MUST_NOT: New backend services, event agent nodes, or protocol tools MUST NOT introduce per-module standard library logger instantiation boilerplate.

## Policy Block

- MUST_NOT New backend services, event agent nodes, or protocol tools MUST NOT introduce per-module standard library logger instantiation boilerplate.

In scope:
- Backend service endpoints and routers managing event processing and task execution.
- Asynchronous agent workflow nodes and task lifecycle tracking components.
- Protocol gateway implementations and modular service tools requiring operational diagnostics.

Out of scope:
- External platform adapters adhering to third-party library conventions that mandate standard library logging integrations.
- Standalone command-line utilities operating outside the main backend service runtime.

## Rationale

- Analysis of 34 files confirms consistent adoption of Loguru across core services, agent nodes, and protocol tool implementations with 0.90 pattern strength.
- Loguru provides a unified logging interface with streamlined exception handling and structured output formatting, reducing code verbosity compared to standard library logger instantiation.
- Adopting a single logging abstraction simplifies operational debugging, log aggregation, and lifecycle tracking across asynchronous workflows.

## Consequences

Positive:
- Eliminates boilerplate module-level logger instantiation across services, agent nodes, and protocol gateways.
- Provides out-of-the-box structured diagnostics, simplified string interpolation, and comprehensive exception traceback capture.
- Unifies operational logging and task lifecycle tracing semantics across asynchronous agent pipelines and service endpoints.

Negative:
- Tight coupling to the Loguru third-party library interface across service and agent execution boundaries.
- Potential coexistence dissonance in codebases where external adapters retain legacy standard library logging idioms.
- Implicit reliance on global logger singleton state which requires deliberate sink and filter management in complex concurrency environments.

## Alternatives

- Standard Library Logging Module (rejected)
  Rejected because: Requires repetitive per-module logger instantiation boilerplate and manual configuration hierarchy management across distributed service nodes.
  When valid: Acceptable in isolated external adapter packages with minimal dependencies or strict standard library adherence constraints.
- Unstructured Standard Output Logging (rejected)
  Rejected because: Lacks standardized severity levels, contextual metadata formatting, exception stack trace handling, and centralized sink management.
  When valid: Never valid for production services, agent orchestration systems, or protocol routers.

## Risks

- Inconsistent logging formats between Loguru-governed service components and external adapters using standard library logging.
  Mitigation: Audit external adapter interfaces and provide bridge configurations where integration with standard library logging hierarchies is necessary.
  Owner: engineering team
- Verbose debug logging in high-throughput asynchronous loops degrading runtime processing efficiency.
  Mitigation: Ensure log levels and emission rates are appropriately configured per environment to prevent log storage exhaustion and performance penalties.
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
- Import the preconfigured logger singleton directly from the logging library rather than reconfiguring handlers or formatters locally within functional units.
- Ensure contextual variables such as task identifiers, event payload descriptors, and routing states are interpolated cleanly or passed as contextual parameters to facilitate traceability.

## Continuation Context


Verify commands:
- Discover the project static analysis and linting configuration scripts from repository manifests, then execute the suite to verify that logging library imports and invocations satisfy codebase standards.
- Identify the test execution script declared in the project configuration and execute the automated test suite to confirm operational logging emits expected diagnostic records without runtime exceptions.
- Execute codebase verification scripts to ensure that prohibited standard library logger instantiations do not exist within service and agent directories governed by this decision.

Accept when:
- All backend services, event agent execution nodes, and service routers import and emit operational diagnostic telemetry through the Loguru logger interface.
- Static analysis verification and automated test suites complete with zero errors and no unhandled exceptions originating from logging invocations.
- The resolved version of the logging dependency in the active environment exactly matches the authoritative project lock artifact.

## Enforcement

- Verified by: Static analysis linting rules configured to detect prohibited logger instantiation patterns across service and agent directories.
- Verified by: Automated test suite execution confirming expected diagnostic message emission and error recording.
- Verified by: Peer code reviews validating compliance with unified logging guidelines during pull request evaluation.
- Violation handling: Continuous integration checks fail when prohibited logging patterns or unauthorized logging dependencies are introduced.
- Violation handling: Pull requests containing non-compliant logging implementations must be remediated prior to merge approval.
- Exception process: Developers must submit an architecture exception request detailing why the unified logger cannot meet specific operational or dependency isolation needs.
- Exception process: Exception requests require sign-off by lead architecture maintainers before diverging logging mechanisms can be introduced.