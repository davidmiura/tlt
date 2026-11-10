---
version: 2
name: 4b9e22ee-f7cc-4bd3-89f8-94d9a8911738-fastapi-health-check-endpoint-pattern-consumer-discover-project-dependency-manifest-lock
description: "FastAPI Health Check Endpoint Pattern: Consumer Discover Project Dependency Manifest Lock"
metadata:
  actual:
    adr_id: 4b9e22ee-f7cc-4bd3-89f8-94d9a8911738
    status: accepted
    candidate_group_id: ed26d008-3769-41d1-91e5-687a0247a9c4
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/event_manager/**
      - tlt/services/tlt_service/**
---

# FastAPI Health Check Endpoint Pattern: Consumer Discover Project Dependency Manifest Lock

Status: proposed
Date: 2025-05-15
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/mcp_services/event_manager/**`
- `tlt/services/tlt_service/**`

## Context

- Microservices and background task services require standardized HTTP probes to verify liveness, readiness, and runtime worker health.
- Service modules contain asynchronous background task managers and queues whose operational state directly impacts service availability.
- FastAPI provides asynchronous route decorators and response mechanisms capable of querying internal manager states and returning structured diagnostics.

## Problem Statement

Without standardized application and router-level health check endpoints, external orchestrators and monitoring systems cannot determine whether a service and its background worker subsystems are actively initialized and capable of processing workloads.

## Decision

1. MUST: The consumer MUST discover the project dependency manifest and lock artifact, verify the exact resolved version of FastAPI, and confirm all routing decorators and response mechanisms match that resolved version's public API specifications.

## Policy Block

- MUST The consumer MUST discover the project dependency manifest and lock artifact, verify the exact resolved version of FastAPI, and confirm all routing decorators and response mechanisms match that resolved version's public API specifications.

In scope:
- All FastAPI application instances and APIRouter components deployed as network-accessible services.
- Routing modules that manage background workers, asynchronous task managers, or persistent queues.

Out of scope:
- Standalone command-line interface utilities lacking an active HTTP listener.
- Internal utility libraries and helper modules that do not define service endpoints.

Exceptions:
- EXC-47-001: A service module operates strictly as a command-line utility or batch worker without an HTTP server runtime.

## Rationale

- Consistent HTTP GET health check endpoints allow container orchestrators and monitoring probes to evaluate service readiness accurately.
- Inspecting subsystem status such as agent availability and queue size enables graceful degradation alerting before catastrophic service failure occurs.
- Standardized error handling and HTTP status code mappings prevent probe false positives and ensure actionable incident escalation.

## Consequences

Positive:
- Uniform service-level and router-level liveness and readiness inspection across all application components.
- Automated detection of degraded worker states, uninitialized managers, and queue backpressure before routing client traffic.
- Consistent JSON status structure and standardized HTTP status codes facilitate integration with external monitoring probes and orchestrators.

Negative:
- Health check handlers that query live subsystem state introduce additional runtime execution overhead during frequent probe intervals.
- Risk of cascading probe timeouts if subsystem status inspection blocks or hangs during degraded states.

## Alternatives

- Process-level or TCP socket health probing without application-level inspection (rejected)
  Rejected because: Fails to verify internal application runtime state, background worker initialization, or queue backpressure, leading to false-positive health reports.
  When valid: Basic network connectivity verification where application runtime state is managed independently.
- Direct database and shared cache querying by external probes rather than service HTTP endpoints (rejected)
  Rejected because: Couples external observability tooling directly to private data stores and bypasses the service HTTP handling and memory-resident subsystem layer.
  When valid: Data-tier health monitoring in infrastructure environments without running application web servers.

## Risks

- Latency amplification or probe timeouts if subsystem status inspection executes blocking operations during degraded states.
  Mitigation: Ensure all dependency and subsystem status checks are non-blocking or bounded by strict microsecond timeouts.
  Owner: Engineering team
- Information leakage regarding internal runtime topology or errors exposed via public health endpoints.
  Mitigation: Restrict health check responses to high-level status classifications and aggregate counters, omitting internal configuration values or credentials.
  Owner: Engineering team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Implement health check handlers with strict internal timeouts on any external or subsystem state evaluation to prevent probe stalls.
- Ensure timestamps returned in health payloads use standard UTC ISO 8601 formatting.
- Separate lightweight liveness verification from comprehensive subsystem readiness diagnostics where deep state evaluation causes resource contention.

## Continuation Context


Verify commands:
- Discover the project test runner and execute integration and unit tests validating HTTP GET requests against registered health endpoints.
- Discover and run the project code inspection tools to verify that all service route modules register health endpoints with structured exception handling.

Accept when:
- All registered health check endpoints respond with HTTP status 200 and valid JSON health payloads when subsystems are operational.
- Health check endpoints respond with HTTP status 503 or structured degraded/unhealthy status dictionaries when dependent managers are unavailable or in error states.
- Static inspection confirms no health check endpoint allows unhandled exceptions to escape without structured status formatting.

## Enforcement

- Verified by: Continuous integration test suites executing HTTP requests against all registered health endpoints.
- Verified by: Static code analysis rules verifying that service entry points and sub-routers register asynchronous health route decorators.
- Verified by: Architecture review during code review workflows for new service modules.
- Violation handling: Pull requests omitting health check endpoints on new service entry points are blocked from merging.
- Violation handling: Health endpoints failing to catch exceptions or return structured health payloads are flagged as critical defects.
- Violation handling: Alerts trigger automated failure notices when health check endpoints return unexpected schema structures.
- Exception process: Submit an architectural exception request detailing why a specific route module or service cannot expose standard HTTP health checks.
- Exception process: Obtain approval from the lead service architect before deploying services without standardized health endpoints.
- Exception process: Document the alternative observability mechanism in the service-level documentation.