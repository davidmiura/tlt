---
version: 2
name: d09fff70-1cb3-41e5-bc8c-af4d9fdbc66a-pydantic-basemodel-for-domain-validation-and-business-rule-encoding-custom-transformation-serialization-logic-complex-types
description: "Pydantic BaseModel for Domain Validation and Business Rule Encoding: Custom Transformation Serialization Logic Complex Types"
metadata:
  actual:
    adr_id: d09fff70-1cb3-41e5-bc8c-af4d9fdbc66a
    status: accepted
    candidate_group_id: 89a6d983-d0c6-439d-b9f8-f482f84c00df
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Pydantic BaseModel for Domain Validation and Business Rule Encoding: Custom Transformation Serialization Logic Complex Types

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/agents/ambient_event_agent/**`
- `tlt/mcp_services/**`
- `tlt/services/tlt_service/**`
- `tlt/shared/**`

## Context

- The system architecture coordinates distributed micro-services, event brokers, transport adapters, and autonomous agent reasoning nodes that exchange complex structured payloads.
- Without centralized declarative business rule encoding, data contracts diverge across components, resulting in unvalidated assumptions, silent state corruption, and scattered defensive checks.
- Static analysis reveals pervasive implementation of Pydantic BaseModel across nineteen modules for domain entities, event envelopes, and tool call schemas to guarantee domain invariants.

## Problem Statement

Distributed components and autonomous agent nodes require consistent, enforceable business rule validation and data serialization across service boundaries. Relying on unstructured dictionaries or procedural validation checks leads to duplicated logic, inconsistent boundary validation, and subtle runtime failures when malformed payloads traverse service interfaces.

## Decision

1. SHOULD: Custom transformation and serialization logic for complex types SHOULD utilize Pydantic field serializer methods to maintain uniform schema representation across transport layers.

## Policy Block

- SHOULD Custom transformation and serialization logic for complex types SHOULD utilize Pydantic field serializer methods to maintain uniform schema representation across transport layers.

In scope:
- All domain entities and aggregate models defined within service boundaries.
- Data transfer objects and request or response contracts exposed across transport adapters.
- Event payloads transmitted through message buses and event brokers.
- Structured schemas bound to language model reasoning tools and agent state tracking.

Out of scope:
- Internal algorithmic loop variables and transient local variables within private helper functions.
- Low-level byte streams, file handles, and binary buffer operations prior to structured decoding.

Exceptions:
- EXC-56-001: Third-party protocol payloads require non-standard binary parsing before conversion to structured domain models.

## Rationale

- Adopting Pydantic BaseModel centralizes domain invariant enforcement directly within model definitions, preventing invalid state from entering the application core.
- Declarative constraints using Field and validator methods decouple rule definition from execution logic, making contracts explicit, testable, and self-documenting.
- Integrating schema validation directly with event serialization and agent reasoning tools ensures end-to-end contract consistency across heterogeneous service boundaries.

## Consequences

Positive:
- Declarative invariant validation guarantees that entities instantiate in a valid state across all service boundaries.
- Explicit schema definitions reduce ambiguity between services, transport adapters, and agent execution nodes.
- Automated serialization and parsing maintain consistent data representation across heterogeneous transport protocols.

Negative:
- Executing validation and serialization on complex hierarchical models introduces runtime overhead during high-throughput payload ingestion.
- Schema evolution requires disciplined migration planning to ensure backwards compatibility across distributed service consumers.

## Alternatives

- Language-standard dataclasses with manual procedural validation functions (rejected)
  Rejected because: Requires authoring and maintaining bespoke validation routines, deserialization handlers, and schema generation logic across each service boundary.
  When valid: When absolute zero-dependency constraints apply in isolated, performance-critical environments.
- Unstructured dictionary payloads validated with imperative assertion blocks (rejected)
  Rejected because: Scatters invariant enforcement across callers, creates brittle implicit schemas, and provides no static type safety.
  When valid: When conducting ephemeral prototyping outside production service architectures.

## Risks

- Performance degradation when repeatedly validating large nested payloads under intense traffic loads.
  Mitigation: Validate payloads strictly at external boundaries and pass validated domain instances across internal calls without re-parsing.
  Owner: Engineering Team
- Breaking schema changes introduced without backward compatibility causing deserialization failures in distributed consumers.
  Mitigation: Enforce schema compatibility checks in the continuous integration pipeline and provide default values for newly added fields.
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
- Define domain models with explicit type annotations on every field, utilizing Field to declare numeric bounds, string constraints, and default factories.
- Place reusable domain schemas in shared domain packages to prevent divergent contract definitions between adapters and services.
- Employ validator decorators for multi-field relational checks and field serializers for canonical data formatting across transport layers.

## Continuation Context


Verify commands:
- Discover and run the project test execution command that targets domain model validation test suites.
- Discover and execute the project static type analysis command to verify that all domain model fields have valid type annotations.
- Discover and execute the project schema verification command to confirm contract compatibility across service boundaries.

Accept when:
- All domain models subclass BaseModel and enforce business invariants via Field constraints or validator methods.
- Automated test suites verifying boundary rejection of invalid payloads pass without failures.
- Static type analysis executes across all model definitions with zero type errors.

## Enforcement

- Verified by: Automated test suites validating payload parsing, boundary rejection, and constraint enforcement.
- Verified by: Static type checking executed during continuous integration workflows.
- Verified by: Peer code reviews verifying model definitions against domain invariant requirements.
- Violation handling: Continuous integration build failure for unvalidated boundary payloads or schema type mismatches.
- Violation handling: Rejection of pull requests introducing unstructured dictionaries at public service interfaces.
- Exception process: Submit an architectural exception request detailing third-party protocol limitations or extreme throughput requirements that preclude declarative schema validation, backed by comprehensive boundary isolation tests.