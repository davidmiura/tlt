---
version: 2
name: 54026c77-64ac-43a2-960a-622881d6c395-discord-library-ui-modal-interaction-and-handler-delegation-modal-classes-not-execute-domain-entity
description: "discord Library UI Modal Interaction and Handler Delegation: Modal Classes Not Execute Domain Entity"
metadata:
  actual:
    adr_id: 54026c77-64ac-43a2-960a-622881d6c395
    status: accepted
    candidate_group_id: 9f0c2e7b-1541-447c-b38e-c2c4c6c0d02c
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# discord Library UI Modal Interaction and Handler Delegation: Modal Classes Not Execute Domain Entity

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`

## Context

- Interactive adapter interfaces require structured input collection from users for event creation and modification workflows.
- Adapter commands and event bridge modules must process interactive submissions without tightly coupling UI components to domain orchestration logic.
- The discord library provides dedicated UI primitives including discord.ui.Modal and discord.ui.TextInput for collecting structured user inputs.

## Problem Statement

Embedding domain orchestration, state transformation, and event dispatch logic directly inside modal callback functions tightly couples UI presentation to application workflows, making testing difficult and duplicating logic across adapter command paths.

## Decision

1. MUST_NOT: Modal UI classes MUST NOT execute domain entity persistence, external network mutations, or complex business logic directly within the on_submit method body.

## Policy Block

- MUST_NOT Modal UI classes MUST NOT execute domain entity persistence, external network mutations, or complex business logic directly within the on_submit method body.

In scope:
- Adapter interaction components and event bridge modules utilizing discord library UI modal primitives.
- Modal dialog workflows capturing structured multi-field user input.

Out of scope:
- Background tasks and event listeners that do not provide or process interactive UI forms.
- Domain core logic modules operating outside external adapter boundaries.

## Rationale

- Inheriting from discord.ui.Modal and declaring discord.ui.TextInput fields standardizes interactive form collection across adapter workflows.
- Delegating modal submission processing to dedicated handler instances preserves modular boundaries and facilitates unit testing.
- Reusing handler contracts across commands and bridge handlers reduces code duplication and standardizes event submission lifecycle handling.

## Consequences

Positive:
- Decouples UI modal presentation definitions from domain workflow and event execution logic.
- Enables independent automated testing of event creation and update handling without instantiating modal components.
- Ensures consistent input collection structures across command interactions and event bridge handlers.

Negative:
- Indirection is introduced by routing modal lifecycle submissions through separate handler classes.
- Handler method signatures must be synchronized with changes in modal input field definitions.

## Alternatives

- Direct Inline Business Logic Execution in Modal Callbacks (rejected)
  Rejected because: Coupling domain operations and persistence directly within UI modal callback methods violates separation of concerns and impedes automated testing without mock UI structures.
  When valid: Trivial dialog interactions requiring no external side-effects, domain processing, or state persistence.
- Multi-Turn Conversational Message Prompts Without Modals (rejected)
  Rejected because: Sequential conversational text prompts introduce complex multi-message state tracking and provide a degraded user experience compared to unified modal dialog inputs.
  When valid: Environments or client interfaces where modal interaction primitives are unsupported.

## Risks

- Interaction timeouts if delegated handler logic exceeds platform callback acknowledgment windows.
  Mitigation: Acknowledge interactions asynchronously or defer interaction responses before executing long-running operations in delegated handlers.
  Owner: Engineering Team
- Contract drift between modal text input field keys and handler method parameter signatures.
  Mitigation: Define typed signatures or structured data models on handler methods to enforce payload contracts.
  Owner: Engineering Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Ensure modal input field values are extracted and passed cleanly as explicit arguments to delegated handler methods.
- Acknowledge or respond to interactions promptly within platform latency limits prior to executing long-running handler operations.

## Continuation Context


Verify commands:
- Discover and execute the repository static analysis and type checking tools to verify compliance of modal classes and handler contracts.
- Discover and execute the repository test runner targeting adapter modal interaction and handler delegation test suites.

Accept when:
- Static type analysis confirms all modal classes inherit from discord.ui.Modal and implement the required handler delegation signatures without syntax or type errors.
- Automated unit and integration test suites pass with all modal submissions delegating execution to dedicated handler methods.

## Enforcement

- Verified by: Continuous integration automated static analysis and type checking suites.
- Verified by: Peer code review on all pull requests modifying adapter interaction components.
- Violation handling: Pull requests that embed domain logic directly within modal callbacks will be blocked until separated into dedicated handlers.
- Exception process: Submit an architectural change request with technical justification demonstrating why modal callback delegation is impractical for the specific interaction.