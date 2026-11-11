---
version: 2
name: 7441f85f-31e5-410d-816a-d7bb9a962233-adoption-of-langchain-core-messages-for-agent-conversation-and-prompt-representation-consumers-discover-repository-dependency-lock-artifact
description: "Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Consumers Discover Repository Dependency Lock Artifact"
metadata:
  actual:
    adr_id: 7441f85f-31e5-410d-816a-d7bb9a962233
    status: accepted
    candidate_group_id: aeb302e6-723a-4cec-9f6d-28fc15080304
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Consumers Discover Repository Dependency Lock Artifact

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Activation

This ADR is active across all ambient agent graph node implementations and state transitions.

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/agents/ambient_event_agent/nodes/**`

## Context

- Agent execution pipelines require structured representations for system directives, human inputs, and model completions within node state.
- Agent base classes and reasoning nodes manipulate conversational context and prompt chains across state transitions.
- A standardized message hierarchy prevents schema drift and inconsistent conversational payloads across heterogeneous agent nodes.

## Problem Statement

Unstructured dictionary or raw string representations of conversational history create serialization inconsistencies, complicate tool binding pipelines, and increase error rates during multi-node agent workflow execution.

## Decision

1. MUST: Consumers MUST discover the repository dependency lock artifact and resolve the exact locked version before invoking framework messaging APIs.

## Policy Block

- MUST Consumers MUST discover the repository dependency lock artifact and resolve the exact locked version before invoking framework messaging APIs.

In scope:
- Agent execution nodes that construct LLM prompts or maintain conversation message history.
- State transitions handling conversational message collections.

Out of scope:
- Internal message queue payloads and external transport contracts that do not interface with LLM reasoning nodes.

## Rationale

- Adopting langchain_core.messages establishes a uniform, strongly-typed interface across agent nodes for constructing prompt contexts.
- Direct integration with framework tool binding and parsing chains simplifies structured reasoning logic and error mitigation.

## Consequences

Positive:
- Standardizes prompt construction and conversation history modeling across all workflow nodes.
- Enables direct compatibility with model tool-binding pipelines and output parsers.
- Eliminates parsing ambiguities between system instructions, human inputs, and model outputs.

Negative:
- Couples agent state data structures directly to the message representations defined by langchain_core.
- Requires state serialization transformations when exporting or persisting messages to external non-Python stores.

## Alternatives

- Represent LLM prompts and message history as raw dictionary structures (rejected)
  Rejected because: Lacks type safety, schema validation, and seamless integration with chain operators and tool binding APIs.
  When valid: Prototyping standalone single-turn scripts without structured agent chains.
- Implement custom in-house message class hierarchies (rejected)
  Rejected because: Reinvents standardized abstractions provided by adopted framework interfaces and breaks interoperability with external model providers.
  When valid: Operating completely outside standard orchestration frameworks with proprietary protocol needs.

## Risks

- Upstream breaking changes in message class schemas across framework versions.
  Mitigation: Pin resolved dependency specifications in the repository lock artifact and verify public API compatibility prior to upgrades.
  Owner: engineering team
- Serialization overhead or failures when logging or caching message state objects.
  Mitigation: Implement dedicated serialization utility routines to safely convert message instances into transport-safe formats.
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
- Base node helper methods should encapsulate state updates for message additions to guarantee timestamping and consistent list updates.
- When building reasoning prompts, construct sequences using SystemMessage for operational guidelines and HumanMessage for contextual event representations.

## Continuation Context


Verify commands:
- Discover and execute the repository static analysis and type checking suite to verify message class imports and usage across agent nodes.
- Discover and execute the repository unit and integration test suite to validate prompt creation and state message tracking.

Accept when:
- All agent nodes manipulating conversational state instantiate messages using langchain_core.messages classes.
- Message sequence definitions in LLM invocations pass structured SystemMessage and HumanMessage instances rather than raw strings or untyped dictionaries.
- The dependency lock verification step confirms exact resolved versions prior to integration.

## Enforcement

- Verified by: Automated static analysis verifying message imports and type usages across agent node modules.
- Verified by: Peer code reviews during pull request evaluations for all agent pipeline changes.
- Violation handling: Pull requests introducing raw dictionary payloads or unapproved message types for prompt history will be blocked from merging.
- Violation handling: Flagged violations must be refactored to use approved langchain_core.messages abstractions.
- Exception process: Submit an architectural review request detailing why framework message abstractions cannot accommodate the integration requirement.
- Exception process: Obtain written approval from the agent architecture governance group before bypassing message standard interfaces.