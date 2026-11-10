---
version: 2
name: 2cfca7a4-bf87-4a02-b980-59494bb20e96-fastmcp-gateway-client-for-mediated-tool-and-data-access-agent-components-not-establish-direct-socket
description: "FastMCP Gateway Client for Mediated Tool and Data Access: Agent Components Not Establish Direct Socket"
metadata:
  actual:
    adr_id: 2cfca7a4-bf87-4a02-b980-59494bb20e96
    status: accepted
    candidate_group_id: a6ce6494-7363-4668-88e4-78fbb3bce226
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/commands/tlt/delete/**
      - tlt/agents/ambient_event_agent/nodes/**
      - tlt/mcp_services/**
      - tlt/scripts/**
      - tlt/services/tlt_service/**
---

# FastMCP Gateway Client for Mediated Tool and Data Access: Agent Components Not Establish Direct Socket

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Activation

This ADR is active for all agent nodes and services performing data retrieval, persistence, and tool operations across the architecture.

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/commands/tlt/delete/**`
- `tlt/agents/ambient_event_agent/nodes/**`
- `tlt/mcp_services/**`
- `tlt/scripts/**`
- `tlt/services/tlt_service/**`

## Context

- Autonomous agent execution nodes require access to domain entities and capabilities distributed across multiple microservices.
- Point-to-point connections introduce tight coupling to individual service network locations, divergent serialization protocols, and fragmented authentication handling.
- Centralizing data access and tool calls behind a uniform transport protocol decouples agent reasoning nodes from backend infrastructure details.
- Standardizing on FastMCP client interfaces ensures consistent session lifecycle management, request tracing, and payload normalization across heterogeneous domain tools.

## Problem Statement

Agent execution nodes previously required ad-hoc integration code and individual network addressing for each backend service, creating fragile couplings and inconsistent request error handling. This architecture requires a unified, protocol-driven data access pattern that abstracts service discovery and contract mapping behind a single gateway transport.

## Decision

1. MUST_NOT: Agent components MUST_NOT establish direct socket, database, or point-to-point HTTP connections to downstream domain services bypassing the centralized gateway transport.

## Policy Block

- MUST_NOT Agent components MUST_NOT establish direct socket, database, or point-to-point HTTP connections to downstream domain services bypassing the centralized gateway transport.

In scope:
- All autonomous agent execution nodes interacting with domain entity services.
- Service integrations invoking tool-based data queries or mutation operations.

Out of scope:
- Intra-service domain logic and direct database queries within a bounded service context.
- High-throughput bulk data streaming pipelines requiring raw byte protocols.

Exceptions:
- EXC-30-001: Emergency diagnostic scripts require direct service interrogation during gateway outage recovery.

## Rationale

- Adopting FastMCP client with StreamableHttpTransport provides standard protocol interfaces for tool execution and structured resource access across services.
- Routing operations through a centralized gateway abstracts backend service topology and centralizes cross-cutting concerns including access control and logging.
- Parameter mapping and payload validation isolate agent decision structures from downstream schema requirements.

## Consequences

Positive:
- Uniform access interface standardizes tool execution and resource retrieval across heterogeneous domain services.
- Centralized gateway facilitates unified access policy enforcement, telemetry collection, and auditing.
- Decouples agent execution logic from backend service physical network topology and port allocations.

Negative:
- Introduces an additional network hop and payload serialization overhead for all service operations.
- The centralized gateway represents a critical dependency and potential operational bottleneck for agent workflows.
- Requires explicit client parameter mapping logic to translate generic agent action payloads into service tool contracts.

## Alternatives

- Direct point-to-point HTTP client calls from agent nodes to individual domain services (rejected)
  Rejected because: Distributes network topology management, tightly couples agent executors to service infrastructure, and duplicates security and session handling across nodes.
  When valid: Simple standalone deployments where an intermediary gateway adds unnecessary operational overhead.
- Direct shared database access across services and agents (rejected)
  Rejected because: Violates service encapsulation boundaries, bypasses business validation rules, and leads to concurrent state corruption across distributed components.
  When valid: Monolithic architectures with centralized transaction management and shared schemas.

## Risks

- Centralized gateway failure or network partition blocks all agent data access.
  Mitigation: Implement circuit breakers, client retry policies with exponential backoff, and gateway health check endpoints.
  Owner: engineering team
- Schema drift between client payload preparation and gateway tool signatures causing execution failures.
  Mitigation: Maintain strict contract validation and automated contract integration tests across service boundaries.
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
- Implement transport instantiation within an asynchronous context manager to ensure socket and connection resources are released immediately following tool execution.
- Configure environment-based URL discovery for the gateway client endpoint to accommodate development, staging, and production network topologies without modifying code.
- Structure tool mapping handlers to inspect and strip internal orchestrator dispatch keys prior to forwarding parameter dictionaries to downstream tool invocations.

## Continuation Context


Verify commands:
- Inspect the workspace configuration to identify the repository test runner, then execute the test suite covering agent executor nodes and gateway integration.
- Run static analysis checks defined in the repository automation configuration to detect any direct service imports or bypasses of the gateway transport.
- Execute integration suites against mock gateway endpoints to validate payload argument preparation and tool mapping.

Accept when:
- All agent data access operations and tool executions route exclusively through the gateway client transport.
- Static analysis validates that no direct service client connections exist outside the gateway transport layer.
- Execution histories record complete request and response lifecycles for every gateway invocation without parameter validation errors.

## Enforcement

- Verified by: Continuous integration test suites verifying gateway client dispatch and tool argument transformations.
- Verified by: Static code analysis verifying absence of direct domain service network calls within agent nodes.
- Verified by: Peer code reviews for all agent execution node changes.
- Violation handling: Automated build checks fail on direct cross-service connections bypassing the gateway.
- Violation handling: Pull requests containing unmediated service access patterns are blocked until refactored.
- Exception process: Submit an architectural review request documenting the latency or functional constraints justifying direct service communication.
- Exception process: Approval must be secured from the architectural review committee prior to merging direct integration code.