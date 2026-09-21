# dotenv for Runtime Environment Configuration Management: Service Entry Points Invoke Load Dotenv

Status: proposed
Date: 2025-05-14
Deciders: Detection Pipeline (automated)

## Context

- Microservices, gateway proxies, and integration adapters across the repository require environment-specific operational parameters including network ports, upstream URLs, storage paths, and logging verbosity.
- Services must be capable of executing in local development, automated testing, and multi-tier production environments without code modification.
- Third-party credentials and access tokens must remain externalized from the codebase to prevent accidental leakage in source repositories.

## Problem Statement

Dispersed microservices and adapter components require consistent, secure access to runtime configuration across varied deployment environments without hardcoding sensitive tokens, network addresses, or file paths into application source code.

## Decision

1. MUST: Service entry points MUST invoke load_dotenv prior to instantiating application servers, proxy clients, or external service connections.

## Policy Block

- MUST Service entry points MUST invoke load_dotenv prior to instantiating application servers, proxy clients, or external service connections.

In scope:
- Applies to all standalone microservices, protocol gateways, and external integration adapters requiring runtime configuration.
- Applies to all operational configuration parameters including service endpoints, listener ports, logging thresholds, local data directories, and API credentials.

Out of scope:
- Does not apply to immutable compile-time constants or domain schemas that do not vary across execution environments.
- Does not apply to transient per-request parameters or dynamic session metadata.

Exceptions:
- EXC-37-001: Containerized runtime environments where environment variables are directly injected into process memory by orchestration platforms.

## Rationale

- Adopting dotenv for tiered environment loading allows developers to maintain consistent local configuration workflows while honoring runtime environment variable overrides in deployed stages.
- Using os.getenv with safe default fallbacks for operational parameters ensures service components start up reliably in development without exhaustive manual configuration.
- Omitting default values for authentication credentials prevents accidental operation in insecure or unauthenticated states.

## Consequences

Positive:
- Decouples application build artifacts from environment-specific configuration topology.
- Enables predictable local development through automated environment file ingestion without manual export steps.
- Guarantees credential protection by strictly separating secret provisioning from source code.

Negative:
- Missing environment variables can lead to silent fallback to defaults during deployment if assertions are not enforced at startup.
- Configuration parameter extraction distributed across multiple files increases the risk of inconsistent key naming across services.
- Requires discipline to keep tiered environment definition files synchronized with service parameter additions.

## Alternatives

- Hardcoded in-source configuration constants (rejected)
  Rejected because: Exposes sensitive operational parameters and credentials in repository history, preventing identical artifacts from executing across distinct runtime environments.
  When valid: Static mock fixtures within isolated unit test suites.
- Centralized remote configuration service registry (rejected)
  Rejected because: Introduces an external network dependency and deployment coupling for lightweight standalone service processes.
  When valid: Large-scale distributed systems requiring dynamic parameter reconfiguration without process restarts.

## Risks

- Silent fallback to development defaults masking missing production environment variables.
  Mitigation: Enforce startup verification assertions that fail immediately when mandatory production environment variables are missing.
  Owner: Engineering Team
- Inconsistent environment variable naming across independently maintained services.
  Mitigation: Maintain centralized configuration schema definitions and standardized environment variable dictionaries.
  Owner: Platform Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Bootstrap configuration loading as the earliest operational step in service entry points prior to importing or initializing network-dependent components.
- Structure environment file lookups to prioritize specific runtime tier definitions over baseline project defaults.

## Continuation Context


Verify commands:
- Discover the project test runner from repository configuration manifests and execute the test suite covering service initialization and configuration loading.
- Discover and run repository static analysis tools to verify that credential extractions do not define hardcoded fallback strings.

Accept when:
- Configuration bootstrapping successfully resolves runtime parameters via the configuration library during service startup across all test environments.
- Service initialization routines fail fast with informative diagnostics when required security credentials are omitted from the environment.
- All non-secret configuration options default to safe local values when environment variables are unset.

## Enforcement

- Verified by: Automated test suites validating configuration loading and default parameter assignment under varying environment states.
- Verified by: Static analysis lint checks identifying hardcoded secret defaults and unvetted environment access patterns.
- Verified by: Peer code review for all new service entry point and adapter initialization modules.
- Violation handling: Pull requests introducing hardcoded secret defaults or unhandled missing credentials will be blocked by continuous integration.
- Violation handling: Missing mandatory configuration parameters will trigger immediate process exit with clear error reporting during service bootstrap.
- Exception process: Submit an architectural review request documenting why standard environment configuration resolution cannot be used.
- Exception process: Obtain approval from the platform engineering lead and security team prior to deploying alternative configuration loading mechanisms.