---
version: 2
name: bd4b9b44-1571-4cb3-ad17-7d2b9ad517e8-adoption-of-tlt-agents-ambient-event-agent-state-state-for-agent-state-management-execution-nodes-not-maintain-persistent-out
description: "Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Execution Nodes Not Maintain Persistent Out"
metadata:
  actual:
    adr_id: bd4b9b44-1571-4cb3-ad17-7d2b9ad517e8
    status: accepted
    candidate_group_id: 92a00aeb-12f9-4606-b2e1-cb0eea1f0284
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/**
---

# Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Execution Nodes Not Maintain Persistent Out

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/agents/ambient_event_agent/**`

## Context

- Ambient event agent workflows execute through discrete asynchronous processing stages including initialization, external interface handling, and message dispatch.
- Execution nodes and routing controllers require consistent access to lifecycle status, rate-limiting metadata, and tool configurations across processing iterations.
- Decoupled processing nodes require a canonical data exchange format to prevent inconsistent ad-hoc state structures across pipeline boundaries.

## Problem Statement

Asynchronous agent workflows that involve multi-step initialization, third-party service messaging, and conditional routing risk state fragmentation and contract drift when individual nodes manage private or inconsistent state schemas across execution boundaries.

## Decision

1. MUST_NOT: Execution nodes MUST NOT maintain persistent out-of-band workflow status across execution cycles outside of the structured state object.

## Policy Block

- MUST_NOT Execution nodes MUST NOT maintain persistent out-of-band workflow status across execution cycles outside of the structured state object.

In scope:
- All asynchronous node implementations within the ambient event agent subsystem.
- Routing and decision controllers managing execution transitions for agent workflows.

Out of scope:
- Standalone utility libraries without workflow state responsibilities.
- Independent external client adapters operating outside the agent execution pipeline.

## Rationale

- Evidence across interface nodes, initialization nodes, and router modules confirms that all pipeline stages depend on the shared state module to coordinate execution metadata and pending requests.
- A single typed state object allows router functions to make deterministic routing decisions without inspecting external side-channel stores.
- Standardizing state structure facilitates centralized error handling, lifecycle monitoring, and debug message capture across asynchronous nodes.

## Consequences

Positive:
- Establishes a uniform contract for all agent pipeline nodes and transition routers.
- Simplifies execution tracing and observability by maintaining unified execution context in a single state object.
- Eliminates fragmented out-of-band communication paths across asynchronous agent lifecycle phases.

Negative:
- All node implementations become tightly coupled to the central state schema definition.
- Evolution of the state schema requires coordination across multiple node handlers and routing functions.
- Risk of state bloat if domain-specific fields are accumulated indiscriminately in the shared state dictionary.

## Alternatives

- Direct parameter passing between individual execution node functions (rejected)
  Rejected because: Direct parameter passing creates expanding argument lists and fragile interfaces across multi-step asynchronous processing stages.
  When valid: When workflow execution consists of simple two-step linear operations with immutable data.
- External distributed database persistence between every node transition (rejected)
  Rejected because: External persistence between every node step introduces unnecessary network latency and database contention for short-lived agent lifecycle iterations.
  When valid: When workflow tasks require long-lived distributed durability across system restarts between processing steps.

## Risks

- Accumulation of unrelated domain fields within the central state contract leading to monolithic state bloat.
  Mitigation: Decompose large state representations into modular typed sub-schemas within the central state module.
  Owner: engineering team
- Concurrent asynchronous mutations causing race conditions or inconsistent updates to shared state fields.
  Mitigation: Enforce sequential node execution through the router to ensure single-writer mutations at each processing stage.
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
- When introducing new workflow nodes, implement the asynchronous execution contract accepting and returning the canonical state structure.
- Group specialized operational state into structured sub-dictionaries or sub-models within the state contract to prevent top-level namespace collisions.

## Continuation Context


Verify commands:
- # Discover and execute project static analysis and type checking across agent modules
- # Discover and run the automated test suite covering agent node execution and routing transitions

Accept when:
- All agent execution node contracts accept and return the canonical AgentState type without type checking errors.
- All route transition functions derive routing decisions exclusively from fields declared in the shared state contract.
- Repository test suites for agent workflow execution and state transitions pass without regressions.

## Enforcement

- Verified by: Automated static type analysis verifying function signatures across all node and router implementations.
- Verified by: Continuous integration test suite validating agent state mutation during end-to-end execution cycles.
- Verified by: Peer code review required for any pull request modifying the shared state schema or node execution contracts.
- Violation handling: Pull requests introducing out-of-band state mutation or alternative state schemas are blocked at continuous integration.
- Violation handling: Violations identified in code review must be refactored to consume and return the canonical state contract before merge.
- Exception process: Submit an architectural review request detailing why an isolated workflow stage requires an independent state structure.
- Exception process: Obtain approval from the lead engineer responsible for agent subsystem architecture before bypassing shared state contracts.