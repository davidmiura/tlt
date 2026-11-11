---
version: 2
name: c342ec3c-c018-49eb-8573-9190bdcd9dd9-environment-variable-configuration-sourcing-via-os-getenv-and-load-dotenv-configuration-variables-requiring-numeric-boolean-structured
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Configuration Variables Requiring Numeric Boolean Structured"
metadata:
  actual:
    adr_id: c342ec3c-c018-49eb-8573-9190bdcd9dd9
    status: accepted
    candidate_group_id: e6112258-c53a-4433-a89b-4d7fee142324
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Configuration Variables Requiring Numeric Boolean Structured

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

## Context

- Distributed microservices, gateway routers, client adapters, and execution nodes require operational configuration including service URLs, transport ports, file storage directories, and authentication secrets.
- Deployments span heterogeneous execution environments where fixed network topologies and static file paths cause configuration drift and runtime failures.
- The codebase across twenty-three modules establishes a uniform convention of querying runtime environment variables with local defaults for non-secret operational settings and strict lookups for credentials.

## Problem Statement

Decoupling runtime configuration from application code is necessary to prevent deployment-specific hardcoding, support autonomous local development, and protect sensitive authentication credentials across distributed microservices.

## Decision

1. MUST: Configuration variables requiring numeric, boolean, or structured types MUST perform type casting and format validation immediately upon extraction from string-based environment variables.

## Policy Block

- MUST Configuration variables requiring numeric, boolean, or structured types MUST perform type casting and format validation immediately upon extraction from string-based environment variables.

In scope:
- All microservices, client adapters, gateway proxies, and background agent nodes within the distributed runtime.
- All configuration parameters defining network locations, communication ports, filesystem paths, runtime environments, log levels, and authentication secrets.

Out of scope:
- Static algorithmic constants and immutable internal protocol enumeration definitions that do not vary across runtime environments.

## Rationale

- Decoupling configuration parameters into environment variables adheres to twelve-factor principles, allowing identical container images and service packages to run across multiple environments.
- Providing sensible local defaults for ports, endpoints, and storage paths enables engineers to initialize services locally without complex environment scaffolding.
- Enforcing explicit omission of defaults for security credentials prevents accidental exposure and enforces strict credential injection in secure environments.

## Consequences

Positive:
- Enables twelve-factor application portability across development, testing, and production environments without modifying source code.
- Provides deterministic local execution through standardized fallback values for service endpoints, ports, and storage directories.
- Mitigates the risk of credential exposure by preventing default values for sensitive authentication tokens.

Negative:
- Scattered environment variable lookups across multiple service files can obscure the comprehensive inventory of required configuration parameters.
- Absence of centralized startup validation risks deferred casting failures if environment variables contain unexpected string formats.

## Alternatives

- Centralized configuration schema objects with unified data validation (deferred)
  Rejected because: A shared centralized configuration schema introduces coupling across independent microservice deployment boundaries where individual services require autonomy.
  When valid: Valid when services are consolidated into a unified runtime or share a dedicated configuration validation package.
- Hardcoded configuration constants in application modules (rejected)
  Rejected because: Hardcoded constants prevent multi-environment deployment portability, violate twelve-factor principles, and risk exposing sensitive credentials in source repositories.
  When valid: Never valid for distributed services requiring environment-specific network bindings or access to secure credentials.

## Risks

- Inconsistent fallback values across services interacting with shared storage or network boundaries.
  Mitigation: Standardize service endpoint defaults and data directory conventions across service documentation and template definitions.
  Owner: engineering team
- Runtime parsing failures caused by malformed or improperly formatted string environment variables.
  Mitigation: Apply immediate type casting and format validation guards at module initialization to halt execution on invalid environment inputs.
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
- Execute environment file hydration calls at the earliest entrypoint phase before importing modules that depend on runtime configuration.
- Wrap directory paths retrieved from environment variables in standard filesystem path objects rather than performing raw string operations.

## Continuation Context


Verify commands:
- Discover and execute the repository static analysis and configuration verification scripts to validate that all service endpoints and directory paths are read via environment variable accessors.
- Discover and execute the repository test suite with environment variables unset to confirm that default fallbacks allow local startup and that secret tokens fail fast.
- Discover the dependency manifest and authoritative lock artifact to verify all declared runtime environment and configuration libraries match the exact locked versions.

Accept when:
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

## Enforcement

- Verified by: Automated static analysis checks detecting hardcoded URLs, IP addresses, local directory paths, and credential literals.
- Verified by: Peer code review validating compliance with environment variable naming conventions and fallback standards.
- Violation handling: Pull requests containing hardcoded operational endpoints or credentials fail automated quality gates.
- Violation handling: Violations must be refactored to use standard environment variable extraction before merging.
- Exception process: Exceptions for non-standard configuration sourcing require architectural review and formal approval.
- Exception process: Approved exceptions must be recorded with justification and targeted remediation milestones.