# BaseNode Contract Adoption for Agent Workflow Execution: Nodes Record Lifecycle Progression Through Update

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Activation

This architecture decision record is active continuously across all agent workflow node authoring, review, and execution processes.

## Context

- Agent orchestration in the ambient event agent subsystem requires coordinated, sequential execution across diverse tasks including configuration loading, service connectivity, rate limiting, and external channel dispatch.
- Without a standardized component contract, individual workflow steps risk implementing divergent error handling, bespoke telemetry recording, and incompatible state access conventions.
- Subclassing the internal BaseNode module establishes a uniform execution protocol where each processing node receives, mutates, and returns a shared AgentState structure.
- Observed implementations demonstrate consistent usage of BaseNode helper methods such as update_state_metadata, log_execution, and handle_error to maintain pipeline observability across distinct operational steps.

## Problem Statement

Multi-step agent workflows require consistent lifecycle management, state propagation, and fault recovery across heterogeneous execution nodes. Without an architectural contract, workflow nodes develop fragmented state mutation patterns and bespoke error handling, hindering pipeline observability and composability.

## Decision

1. MUST: Nodes MUST record lifecycle progression through update_state_metadata, setting the status and processing step attributes on AgentState during execution.

## Policy Block

- MUST Nodes MUST record lifecycle progression through update_state_metadata, setting the status and processing step attributes on AgentState during execution.

In scope:
- Implementation of execution steps and processing nodes within the ambient event agent pipeline.
- Components performing state transitions, lifecycle tracking, and external service communication inside agent workflows.

Out of scope:
- Standalone utility functions, pure mathematical routines, and stateless data parsers that do not manipulate agent execution state.
- External service clients and adapter libraries operating outside the agent workflow node graph.

## Rationale

- Standardizing on BaseNode guarantees that all workflow steps adhere to a uniform coroutine signature, enabling consistent chaining and error propagation within the agent runtime.
- Centralizing state metadata updates and error handling through BaseNode methods prevents divergent logging formats and ensures that agent state transitions remain auditable.
- Encapsulating isolated operational duties within discrete BaseNode implementations preserves node independence while maintaining shared state contracts across the pipeline.

## Consequences

Positive:
- Uniform asynchronous interface across all agent workflow nodes simplifies orchestrator dispatch and sequential composition.
- Standardized metadata updates and error handling provide consistent observability and fault isolation across pipeline stages.
- Clear separation of responsibilities within modular node classes enhances testability and maintainability of individual agent capabilities.

Negative:
- Workflow nodes are structurally coupled to the shared AgentState schema and BaseNode base class hierarchy.
- Passing a mutable state dictionary across execution nodes increases the risk of unintended cross-step side effects if state keys collide.
- Coroutines that swallow exceptions to update state status require strict upstream checking by orchestrators to prevent silent partial failures.

## Alternatives

- Functional pipeline composed of standalone coroutine functions without inheritance (rejected)
  Rejected because: Standalone functions require redundant boilerplate for lifecycle logging, error handling, and state metadata management across each processing step.
  When valid: Valid for stateless, short-lived transformation chains that do not require stateful rate limiting or centralized execution telemetry.
- Monolithic orchestrator managing all execution steps within a single agent class (rejected)
  Rejected because: Monolithic handlers violate single-responsibility boundaries, complicating testing and rate-limiting across disparate integrations.
  When valid: Valid for trivial agents with only one or two linear processing steps.

## Risks

- Unchecked mutations to AgentState across multiple nodes can introduce race conditions or schema drift.
  Mitigation: Enforce strict schema definitions on AgentState and implement validation checks during state transitions.
  Owner: Agent Architecture Team
- Node-level exception swallowing via handle_error may allow downstream nodes to execute with corrupted state unless status checks are enforced.
  Mitigation: Verify agent status at orchestrator dispatch boundaries before scheduling subsequent workflow nodes.
  Owner: Agent Runtime Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- When constructing a new workflow node, ensure the string identifier passed to superclass initialization matches the canonical node designation used in pipeline orchestration configuration.
- Implement rate limiting and scheduling verification inside the node execute loop prior to invoking external network operations or third-party service adapters.
- Verify that state mutations preserve immutable event identifiers and retain existing metadata keys across processing steps.

## Continuation Context


Verify commands:
- Discover the configured test runner from project metadata and execute the test suite validating BaseNode contract compliance and execute coroutine behavior.
- Locate the repository type verification configuration and run type checking to verify that all node execute implementations conform to the AgentState input and return signatures.
- Discover the linting and static analysis tool from project configuration and verify that all workflow node classes subclass BaseNode and invoke superclass initialization.

Accept when:
- All workflow node implementations inherit from BaseNode and successfully execute state transformation unit tests without unhandled exceptions.
- Static type analysis confirms that all execute coroutines strictly accept and return AgentState.
- Integration tests confirm that execution steps record state metadata transitions and error statuses under simulated failure conditions.

## Enforcement

- Verified by: Automated continuous integration checks executing contract tests and static type validation on all workflow nodes.
- Verified by: Peer code review verifying adherence to BaseNode inheritance, error handling conventions, and state mutation discipline.
- Violation handling: Continuous integration pipeline fails the build when workflow nodes deviate from the BaseNode contract or fail type checks.
- Violation handling: Pull requests introducing non-compliant workflow steps or bypassed lifecycle methods are blocked from merging.
- Exception process: Exceptions require documented architectural justification and formal sign-off from the Agent Framework Maintainers.
- Exception process: Any approved exception must be recorded in an architecture decision addendum detailing alternative telemetry and state guarantees.