# Pydantic Adoption for Structured Domain and Event Validation: Boundary Transformation Payload Serialization Dictionary Representations

Status: proposed
Date: 2025-05-15
Deciders: Detection Pipeline (automated)

## Context

- Heterogeneous event sources including messaging integrations, scheduled timers, and external cloud events deliver unstructured payloads that require strict validation before entering core workflows.
- Agent execution states and microservice domain entities require strongly typed data structures to maintain state consistency across asynchronous task queues.
- Decoupled services need uniform serialization and deserialization mechanisms to exchange event representations reliably across process boundaries without data corruption.

## Problem Statement

Unvalidated or inconsistently structured event payloads and domain data introduce runtime attribute errors, type mismatches, and schema drift across asynchronous processing boundaries. Without a standardized data validation and modeling framework, components must rely on manual dictionary key verification and defensive programming, increasing maintenance overhead and the risk of unhandled ingestion failures.

## Decision

1. MUST: Boundary transformation and payload serialization to dictionary representations MUST be executed via the model_dump method rather than custom dictionary parsing or legacy serialization methods.

## Policy Block

- MUST Boundary transformation and payload serialization to dictionary representations MUST be executed via the model_dump method rather than custom dictionary parsing or legacy serialization methods.

In scope:
- All domain models representing business entities, agent context states, and service task structures.
- All incoming and outgoing event payloads processed across asynchronous queues and service boundaries.

Out of scope:
- Internal ephemeral scratch variables and primitive loop counters within local function scopes.
- Low-level system utility scripts and infrastructure automation routines that do not exchange domain entities.

Exceptions:
- EXC-20-001: Streaming raw binary data or unparsed byte streams where schema validation is deferred to downstream consumers.

## Rationale

- Standardizing on Pydantic BaseModel provides declarative, type-safe data validation that fails fast at boundary ingress rather than deep inside asynchronous pipelines.
- Using Field constructs and enumerated types enables expressive schema definition with built-in boundary checks and factory defaults.
- Standard model serialization via model_dump ensures consistent dictionary and structured representation across service task queues and logging frameworks.

## Consequences

Positive:
- Immediate detection and rejection of malformed incoming payloads at service and agent boundaries.
- Consistent type inference and automated validation across domain entities and state models.
- Uniform payload transformation and serialization reducing defensive coding and parsing boilerplate.

Negative:
- Computational overhead incurred during runtime validation of large or high-frequency event payloads.
- Coupling of domain state definitions to a specific schema validation library API surface.
- Schema migration complexity when model definitions evolve across distributed components.

## Alternatives

- Standard Library Dataclasses without Runtime Validation (rejected)
  Rejected because: Standard dataclasses lack native runtime coercion, field-level boundary validation, and deep serialization capabilities required for untrusted external payloads.
  When valid: Valid in internal modules where data is guaranteed to be well-typed and performance constraints prohibit validation overhead.
- Manual Dictionary Manipulation and Custom Key Assertion (rejected)
  Rejected because: Manual dictionary parsing leads to brittle boilerplate, frequent runtime lookup failures, and the absence of standardized schema contracts.
  When valid: Valid for ad-hoc one-off migration scripts or minimal utilities with no external contract dependencies.

## Risks

- Validation overhead under high-volume event ingestion causing increased processing latency.
  Mitigation: Profile validation hot paths and configure schema models to skip redundant nested re-validations when passing trusted internal boundaries.
  Owner: Core Platform Engineering Team
- Breaking API changes across major library releases affecting serialization method signatures.
  Mitigation: Adhere to the lock-version discovery policy and maintain centralized wrapper or adapter conventions for core serialization calls.
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
- Define all model schemas with explicit type annotations on every field, utilizing factory declarations for mutable defaults such as collections and dynamic timestamps.
- Ensure ingress boundaries translate external payload dictionaries into validated model instances immediately upon entry before queueing or processing.

## Continuation Context


Verify commands:
- Discover the project test suite runner from repository manifests and execute validation tests against all domain model and context definitions.
- Discover the static analysis tool configuration from repository manifests and execute type verification across all data model declarations.

Accept when:
- All domain entities, event contexts, and service payloads instantiate and validate successfully under the test suite.
- Static type analysis passes with zero type errors across all model definitions and their usage sites.
- Serialization operations produce valid structured payloads matching defined schema contracts without throwing attribute errors.

## Enforcement

- Verified by: Automated test suites executed in continuous integration verifying model validation and serialization behavior.
- Verified by: Static type checking integrated into continuous verification pipelines to validate schema annotations.
- Verified by: Peer code review confirming that all new domain entities and boundary payloads inherit from BaseModel.
- Violation handling: Pull requests containing untyped dictionary processing at service boundaries or models lacking validation are blocked from merging.
- Violation handling: Identified runtime schema mismatches generate alert events requiring remediation to conform to model contracts.
- Exception process: Submit an architectural review request outlining the necessity of bypassing model validation for specific high-throughput or unstructured endpoints, requiring approval from the Core Platform Engineering Team.