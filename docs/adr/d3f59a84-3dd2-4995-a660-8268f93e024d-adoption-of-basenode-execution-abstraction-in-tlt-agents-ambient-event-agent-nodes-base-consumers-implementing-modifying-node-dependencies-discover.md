---
version: 2
name: d3f59a84-3dd2-4995-a660-8268f93e024d-adoption-of-basenode-execution-abstraction-in-tlt-agents-ambient-event-agent-nodes-base-consumers-implementing-modifying-node-dependencies-discover
description: "Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Consumers Implementing Modifying Node Dependencies Discover"
metadata:
  actual:
    adr_id: d3f59a84-3dd2-4995-a660-8268f93e024d
    status: accepted
    candidate_group_id: 8338cac3-2465-4de2-8a0d-e2367dec5e66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Consumers Implementing Modifying Node Dependencies Discover

Status: proposed
Date: 2025-05-15
Deciders: Detection Pipeline (automated)

## Activation

This Architecture Decision Record is always active for all agent node implementations within the ambient event agent subsystem.

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/agents/ambient_event_agent/nodes/**`

## Context

- The ambient event agent coordinates state transitions and event processing across diverse operational stages including initialization, event ingestion, and external channel communication.
- Individual workflow nodes require consistent execution semantics, structured error containment, and unified telemetry logging across all pipeline steps.
- Adopting a shared base class module standardizes state mutation, error recovery, and execution tracking across sequential and asynchronous processing steps.

## Problem Statement

Without a standardized base class and execution contract for workflow nodes, agent pipeline components implement bespoke state handling, varied logging patterns, and inconsistent error recovery mechanisms, increasing the likelihood of silent failures and uncoordinated state corruption during complex event lifecycles.

## Decision

1. MUST: Consumers implementing or modifying node dependencies MUST discover the ecosystem lock artifact and verify the exact resolved dependency versions prior to introducing external libraries.

## Policy Block

- MUST Consumers implementing or modifying node dependencies MUST discover the ecosystem lock artifact and verify the exact resolved dependency versions prior to introducing external libraries.

In scope:
- Workflow node classes implementing operational phases of the ambient event agent pipeline.
- Components managing state transitions, event monitoring, external adapter messaging, or agent lifecycle orchestration.

Out of scope:
- Standalone data transfer objects, external schema definitions, and domain models.
- Leaf utility functions and stateless helper routines that do not participate in workflow state progression.

## Rationale

- Static evidence across node implementations reveals unanimous inheritance from BaseNode and adherence to the execute contract returning AgentState, demonstrating an established architectural standard.
- Encapsulating lifecycle logging, error reporting, and state metadata updates within BaseNode helper methods eliminates boilerplate across node implementations while ensuring uniform telemetry.
- Asynchronous execution contracts allow non-blocking operations across I/O-bound integrations such as timer evaluations, external protocol interfaces, and event dispatching.

## Consequences

Positive:
- Enforces deterministic state progression and consistent error handling across all agent processing nodes.
- Centralizes node lifecycle telemetry and metadata updates through unified helper methods.
- Simplifies pipeline expansion by providing a well-defined contract for authoring new agent capabilities.

Negative:
- Tightly couples all pipeline stages to the class hierarchy and runtime assumptions of BaseNode.
- Requires all node logic to adhere to shared state object passing rather than fine-grained input and output signatures.

## Alternatives

- Function-based pipeline stages using standalone callable closures rather than class inheritance (rejected)
  Rejected because: Lacks standardized lifecycle hooks, centralized error reporting methods, and persistent node instance configuration
  When valid: Valid in lightweight data transformation pipelines that require no lifecycle tracking or instance-level configuration
- Protocol-based structural typing with independent node implementations (rejected)
  Rejected because: Forces duplicated implementation of logging, error handling, and state metadata management across every node
  When valid: Valid when decoupling pipeline nodes across distinct external libraries where inheritance is prohibited

## Risks

- Changes to BaseNode state management or helper signatures could cascade breaking changes across all node subclasses.
  Mitigation: Maintain strict interface backward compatibility and enforce regression test suites across all node modules.
  Owner: Engineering team
- Overhead of passing full AgentState objects through every node may obscure specific node input and output dependencies.
  Mitigation: Explicitly document required and produced state fields in node docstrings and type annotations.
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
- When implementing a new node subclass, invoke the superclass initializer with a descriptive snake_case identifier that represents the node responsibility.
- Encapsulate execution logic within a structured try-except block that delegates exception recording to handle_error before returning the state object.

## Continuation Context


Verify commands:
- Discover the project test runner and execute the test suite targeting agent workflow nodes to verify BaseNode contract compliance and state propagation.
- Discover the project static analysis or type inspection tool and run type checks to confirm all execute signatures match AgentState input and output contracts.

Accept when:
- All agent workflow node test suites pass without unhandled exceptions or state contract violations.
- Static type verification confirms all workflow nodes implement the asynchronous execute contract with AgentState.

## Enforcement

- Verified by: Static type analysis and automated integration tests verifying BaseNode subclassing and execute contract compliance.
- Verified by: Peer code review for all new agent pipeline node contributions.
- Violation handling: Pull requests introducing node components that do not inherit from BaseNode or that violate the execute contract will be blocked from merging until refactored.
- Exception process: Exceptions require written architectural justification and approval from the principal agent architecture team before bypassing the BaseNode hierarchy.