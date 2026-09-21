# FastAPI Health Check Endpoint Pattern for Subsystem Observability: Health Check Route Handlers Handle Internal

Status: proposed
Date: 2025-07-02
Deciders: Detection Pipeline (automated)

## Context

- Multiple HTTP service endpoints and domain routers implement observability routes to report operational health.
- Services depend on internal asynchronous task and agent management subsystems whose availability dictates overall service readiness.
- Inconsistent health probing across modular routers risks silent subsystem failure and inaccurate liveness reporting by external orchestrators.
- Standardizing health check route declarations enables uniform probing across the application root and sub-routers.

## Problem Statement

Modular services require a standardized mechanism for runtime monitors and orchestrators to probe operational availability and subsystem readiness. Without a unified pattern for health endpoints across application boundaries and modular routers, subsystems may fail silently or report false readiness, leading to degraded task execution and inadequate operational visibility.

## Decision

1. MUST: Health check route handlers MUST handle internal subsystem exceptions gracefully, logging failure details via the structured logger and returning an explicit failure payload or status code.

## Policy Block

- MUST Health check route handlers MUST handle internal subsystem exceptions gracefully, logging failure details via the structured logger and returning an explicit failure payload or status code.

In scope:
- HTTP service boundary entrypoints
- Modular domain routers exposing operational or task execution endpoints
- Subsystems requiring external readiness and liveness inspection

Out of scope:
- Internal utility modules without HTTP endpoint routing
- Data transfer object schema definitions
- Stateless transformation functions

## Rationale

- Evidence demonstrates consistent deployment of health check endpoints across entrypoints and modular sub-routers inspecting internal subsystem state.
- Centralizing readiness checks within dedicated asynchronous route handlers allows external monitoring tools to detect degraded states prior to task assignment.
- Graceful exception handling within health endpoints prevents monitoring probes from causing unhandled server exceptions.

## Consequences

Positive:
- Predictable service readiness and liveness reporting across all modular routing boundaries.
- Early detection of internal subsystem failures and backpressure before task ingestion.
- Standardized payload structures for integration with monitoring and operational metrics aggregators.

Negative:
- Additional maintenance overhead to ensure health checks reflect newly added subsystem dependencies.
- Potential risk of status check failures causing false-positive orchestrator restarts if transient degradation is not handled properly.

## Alternatives

- Rely exclusively on root application ping endpoints without sub-router health checks (rejected)
  Rejected because: Root-only ping endpoints do not evaluate sub-component readiness and allow modular router degradation to go undetected.
  When valid: In minimal microservices containing no internal background managers or modular sub-routers.
- Out-of-band health reporting via external telemetry heartbeats (rejected)
  Rejected because: External heartbeats bypass standard HTTP pull-based orchestrator probes and increase infrastructure complexity.
  When valid: In headless worker processes lacking HTTP listener capabilities.

## Risks

- Health check logic may introduce blocking calls or database contention during high-frequency polling.
  Mitigation: Enforce asynchronous non-blocking probes and cache subsystem status when checks require expensive queries.
  Owner: engineering team
- Degraded status returning non-success HTTP codes may trigger abrupt container restarts during temporary backpressure.
  Mitigation: Configure monitoring orchestrators with appropriate failure thresholds and distinguish between warning and fatal states.
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
- Health check route handlers must be registered using asynchronous route definitions to prevent thread starvation under concurrent monitoring sweeps.
- Subsystem readiness checks should aggregate critical runtime metrics such as queue size and task processing state into the response body.

## Continuation Context


Verify commands:
- $SHELL -c 'test_runner=$(find . -maxdepth 2 -name "*test*" | head -n 1); if [ -n "$test_runner" ]; then echo "Test harness discovered"; fi'
- $SHELL -c 'grep -rE "@(app|router)\.get\(\"/health" .'

Accept when:
- All health check endpoints respond with valid operational status payloads containing health state descriptors.
- Verification suites confirm that uninitialized dependencies produce degraded or error status responses rather than unhandled server crashes.
- Static checks confirm that health endpoints are registered on both application and sub-router boundaries without performing mutating actions.

## Enforcement

- Verified by: Continuous integration test suites verifying endpoint availability and status responses
- Verified by: Static analysis checks verifying health check decorator presence on modular routers
- Verified by: Peer code review for all new router modules
- Violation handling: Pull requests missing health check routes on new HTTP services or routers will fail review approval.
- Violation handling: Build failures triggered by missing or broken readiness endpoints during integration testing.
- Exception process: Architecture review approval documented in service design records for non-HTTP micro-components.