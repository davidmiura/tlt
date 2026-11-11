---
version: 2
name: b6684cb4-0d74-411f-a07f-3883cc444c2b-pydantic-basemodel-for-public-api-and-service-contract-boundaries-public-response-models-outbound-payloads-serialized
description: "Pydantic BaseModel for Public API and Service Contract Boundaries: Public Response Models Outbound Payloads Serialized"
metadata:
  actual:
    adr_id: b6684cb4-0d74-411f-a07f-3883cc444c2b
    status: accepted
    candidate_group_id: 63f40091-32f3-4392-b9da-8c66a16a77bb
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
      - tlt/shared/**
---

# Pydantic BaseModel for Public API and Service Contract Boundaries: Public Response Models Outbound Payloads Serialized

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`
- `tlt/agents/ambient_event_agent/**`
- `tlt/mcp_services/**`
- `tlt/scripts/**`
- `tlt/services/tlt_service/**`
- `tlt/shared/**`

## Context

- External endpoints, event routers, and service boundaries across the monorepo receive heterogeneous inputs from public clients, webhooks, and asynchronous message brokers.
- Absence of uniform boundary data contracts risks runtime attribute errors, defensive type checking scattered across handlers, and payload schema drift.
- The codebase consistently structures external data models, event contexts, and endpoint responses using declarative schema definitions with explicit field-level constraints.

## Problem Statement

External APIs, event consumers, and inter-service tools receive untrusted or polymorphic payloads from external clients and messaging systems. Without a unified contract definition standard, boundary handling suffers from inconsistent validation, scattered defensive assertions, lack of schema documentation, and vulnerabilities to runtime data corruption.

## Decision

1. SHOULD: Public API response models and outbound payloads SHOULD be serialized using the standard model serialization methods provided by the BaseModel class.

## Policy Block

- SHOULD Public API response models and outbound payloads SHOULD be serialized using the standard model serialization methods provided by the BaseModel class.

In scope:
- All public REST endpoint request and response bodies.
- All external webhook, CloudEvent, and message broker payload ingestion schemas.
- All MCP tool and resource public interface parameters and response objects.

Out of scope:
- Internal workflow state dictionaries confined exclusively within private node execution loops.
- Low-level transport protocol configurations and operating system environment parsing.

## Rationale

- Adopting Pydantic BaseModel as the single contract definition framework ensures standardized runtime validation, automated type casting, and clear error reporting at system entry points.
- Field annotations allow engineering teams to express constraints like numerical bounds and descriptions declaratively alongside data models rather than imperatively in controller logic.
- Evidence across 97 files demonstrates reliable usage across event routers, MCP services, and photo processing workflows, showing widespread project alignment.

## Consequences

Positive:
- Establishes deterministic, declarative contract specifications that reject malformed payloads before execution reaches domain services.
- Enforces unified type safety, field constraints, and documentation metadata across public endpoints, MCP services, and event routers.
- Prevents silent schema drift and contract regressions across distributed components sharing boundary structures.

Negative:
- Requires maintaining explicit schema classes and field definitions for every boundary request, response, and event format.
- Introduces computational serialization and validation overhead on high-frequency boundary ingest points compared to raw dictionary access.

## Alternatives

- Ad-hoc runtime dictionary inspection with manual conditional validation (rejected)
  Rejected because: Manual dictionary checking scatters defensive assertions throughout service logic, lacks automated type coercion, and fails to provide declarative schema definitions for external consumers.
  When valid: Valid only in minimal internal utility scripts with no external consumers or cross-service interactions.
- Standard library dataclasses without input validation constraints (rejected)
  Rejected because: Standard dataclasses do not enforce runtime boundary validation or field-level constraint evaluation on deserialization, allowing malformed external data into service logic.
  When valid: Valid for purely internal data containers where inputs are guaranteed to be pre-validated and trusted.

## Risks

- Validation overhead on extremely high-throughput endpoints could increase request latency.
  Mitigation: Profile serialization and deserialization routines at high-throughput ingestion points and use optimized model serialization methods.
  Owner: engineering team
- Strict schema validation may reject external requests containing unexpected or deprecated fields during client upgrades.
  Mitigation: Maintain explicit field deprecation policies and validate backward compatibility with contract integration tests before modifying schemas.
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
- Define all input request bodies, output response representations, and cross-boundary event payloads in dedicated schema modules.
- Use Field descriptors to enforce numeric ranges, required string semantics, and default values directly in model declarations.

## Continuation Context


Verify commands:
- Discover and run the project's contract validation test suite from the repository test configuration to verify that all public API schemas adhere to model validation rules.
- Execute the static type checking and schema linting routines identified in the repository build scripts to confirm type consistency across all BaseModel definitions.

Accept when:
- All public API and service boundary schemas inherit from BaseModel and pass schema validation tests without runtime or structural errors.
- Static type analysis confirms zero type-contract mismatches across public endpoint handlers and their declared request and response models.

## Enforcement

- Verified by: Automated schema validation suites executed during continuous integration pipeline checks.
- Verified by: Static type checking and linter verification confirming all public endpoint handlers declare BaseModel contract types.
- Verified by: Pull request code reviews focusing on public interface and cross-service boundary definitions.
- Violation handling: Pull requests introducing untyped dictionary interfaces or omitting BaseModel schemas on public boundaries are blocked from merging.
- Violation handling: Static analysis and validation test failures fail continuous integration builds immediately.
- Exception process: Submit an architectural exception request detailing why a public or external interface cannot be modeled with declarative BaseModel contracts.
- Exception process: Obtain sign-off from the API architecture review team with documented manual validation guarantees before merging.