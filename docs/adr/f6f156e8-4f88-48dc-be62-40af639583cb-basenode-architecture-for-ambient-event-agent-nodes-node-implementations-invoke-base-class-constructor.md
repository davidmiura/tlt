# BaseNode Architecture for Ambient Event Agent Nodes: Node Implementations Invoke Base Class Constructor

Status: proposed
Date: 2025-05-15
Deciders: Detection Pipeline (automated)

## Activation

This architectural decision record is continuously active across all ambient event agent node implementations.

## Context

- Agent subsystems require structured asynchronous workflows to process incoming events, coordinate interfaces, and initialize external dependencies.
- Ad-hoc asynchronous handling across different pipeline steps leads to fragmented error recovery, inconsistent state transitions, and uncoordinated diagnostics.
- Standardizing node construction around an internal base module provides cohesive lifecycle management and operational consistency.

## Problem Statement

Disparate agent workflow steps, such as event monitoring, external messaging, and initialization, risk inconsistent execution lifecycles, disparate error handling strategies, and divergent state updates when implemented without a standardized node foundation.

## Decision

1. MUST: Node implementations MUST invoke the base class constructor with a unique component identifier string during initialization.

## Policy Block

- MUST Node implementations MUST invoke the base class constructor with a unique component identifier string during initialization.

In scope:
- All discrete workflow steps, event handlers, and interface processors within the agent node subsystem.
- Components responsible for asynchronous agent state inspection, transformation, or lifecycle progression.

Out of scope:
- Stateless pure mathematical or formatting utilities that do not mutate or inspect agent state.
- External protocol adapters operating outside the agent pipeline execution boundary.

## Rationale

- Subclassing BaseNode establishes an enforced operational protocol across all workflow phases, ensuring state transitions and diagnostics are uniformly reported.
- Centralizing error handling and metadata updates within derived nodes prevents unhandled exceptions from terminating the broader pipeline.
- Adopting a common asynchronous execute signature enables pipeline runners to compose and sequence nodes interchangeably.

## Consequences

Positive:
- Enforces consistent error isolation, execution logging, and step tracking across disparate workflow stages.
- Standardizes the asynchronous execution contract, allowing predictable pipeline orchestration and composition.
- Simplifies state progression and debugging through uniform metadata update hooks.

Negative:
- Tight coupling to the internal BaseNode contract and shared AgentState schema structure across all pipeline components.
- Base class changes risk propagating breaking behavioral regressions across all derived node implementations.

## Alternatives

- Standalone functional dispatch handlers without BaseNode inheritance (rejected)
  Rejected because: Lacks standardized error recovery, metadata progression tracking, and unified lifecycle hooks across pipeline stages.
  When valid: Applicable in stateless utility routines that operate outside of the agent state graph.
- Actor-model message-passing framework with independent state mailboxes (rejected)
  Rejected because: Introduces substantial architectural overhead and synchronization complexity incompatible with the centralized AgentState dictionary model.
  When valid: Applicable when nodes require independent thread boundaries or isolated process memory spaces.

## Risks

- Shared state dictionary structure introduces implicit dependencies between pipeline nodes.
  Mitigation: Enforce strict schema validation and typing for AgentState across all node interactions.
  Owner: engineering team
- Unhandled asynchronous task errors could leave the agent in an unresolved processing state.
  Mitigation: Require top-level try-catch blocks delegating to the base error handler inside every execute implementation.
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
- Derived node constructors must initialize the base class with a distinct, descriptive component identifier string.
- State transformations must preserve immutable dictionary keys and update progress status through base class helper methods.
- External network and messaging operations must yield execution asynchronously without blocking the event loop.

## Continuation Context


Verify commands:
- Discover the project verification runner from the repository configuration and execute the automated test suite targeting agent node behaviors.
- Execute the repository linter and static type analyzer according to the project configuration to verify compliance with BaseNode interfaces and AgentState type signatures.

Accept when:
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

## Enforcement

- Verified by: Automated continuous integration test suites verifying node execution contracts and state transformations.
- Verified by: Static type analysis enforcing inheritance from BaseNode and adherence to the AgentState signature.
- Verified by: Mandatory peer code reviews validating lifecycle hook integration and error delegation.
- Violation handling: Automated pull request checks will reject code that introduces workflow nodes bypassing BaseNode or omitting execute implementations.
- Violation handling: Static analysis or runtime failures resulting from improper state handling must be remediated prior to merge approval.
- Exception process: Requests for exceptions must submit a formal architectural justification detailing why the node cannot adopt the BaseNode lifecycle model.
- Exception process: Exceptions require formal review and approval by the system architecture stewards before integration.