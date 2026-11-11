---
version: 2
name: 12232c03-eab4-4b1c-a65e-cd5ea19f1c88-adoption-of-discord-py-for-discord-bot-and-interaction-adapter-architecture-handlers-responding-discord-events-commands-use
description: "Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Handlers Responding Discord Events Commands Use"
metadata:
  actual:
    adr_id: 12232c03-eab4-4b1c-a65e-cd5ea19f1c88
    status: accepted
    candidate_group_id: 50245619-c6da-4a37-a81d-14b49ea7b7c6
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
---

# Adoption of discord.py for Discord Bot and Interaction Adapter Architecture: Handlers Responding Discord Events Commands Use

Status: proposed
Date: 2025-02-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/adapters/discord_adapter/**`

## Context

- The application requires integration with Discord to manage community events, collect feedback, handle administrative registrations, and broadcast reminders
- Discord interactions require low-latency asynchronous processing of gateway events, slash commands, modal dialogs, select dropdowns, and button actions
- A consistent library adoption is required across all adapter modules to prevent fragmented communication protocols and ad-hoc gateway integrations

## Problem Statement

Integrating with Discord without a unified client framework risks fragmented gateway lifecycle handling, duplicate payload serialization, inconsistent command registration, and unstructured UI component lifecycles across adapter services.

## Decision

1. MUST: Handlers responding to Discord events and commands MUST use discord.Interaction response methods to acknowledge user actions asynchronously within platform deadline limits.

## Policy Block

- MUST Handlers responding to Discord events and commands MUST use discord.Interaction response methods to acknowledge user actions asynchronously within platform deadline limits.

In scope:
- All modules and classes within the Discord adapter boundary interacting with the Discord Gateway, application commands, or user interface components
- Scheduled background routines managing periodic checks or automated reminder broadcasts within the Discord client runtime

Out of scope:
- Core domain logic and data entities operating outside of the Discord adapter boundary
- Independent HTTP API endpoints and services that do not communicate with the Discord Gateway or interface with Discord users

## Rationale

- Adopting discord.py provides a comprehensive, production-tested asynchronous framework that encapsulates Discord Gateway connections, heartbeats, and rate limiting
- The discord.ui and discord.app_commands abstractions enable structured implementation of modern slash commands, modals, buttons, and select menus with declarative event callbacks
- The discord.ext.tasks module provides clean background execution loops integrated natively into the client asynchronous event loop

## Consequences

Positive:
- Standardizes slash command definitions, modal dialogs, and interactive component views across the entire adapter layer
- Provides native asynchronous task loop scheduling and automated gateway reconnection handling out of the box
- Separates Discord-specific presentation concerns such as embeds and views from underlying domain service workflows

Negative:
- Tightly couples the adapter layer to the async event loop lifecycle and internal object models of discord.py
- Requires ongoing adaptation when upstream platform interaction contracts evolve within the library ecosystem
- Testing interactive components and modal callbacks requires mock interaction objects and simulation of gateway states

## Alternatives

- Direct raw HTTP and WebSocket gateway client implementation (rejected)
  Rejected because: Requires maintaining manual Discord Gateway heartbeat protocols, payload serialization, and interaction state management, drastically increasing maintenance burden.
  When valid: When running in severely constrained environments where third-party asynchronous client libraries cannot be introduced.
- Legacy prefix message-parsing command architecture (rejected)
  Rejected because: Lacks native interactive UI components, ephemeral response capabilities, and modern slash command autocomplete facilities provided by Discord interaction models.
  When valid: When integrating with legacy servers or older bot frameworks that do not support modern application command trees.

## Risks

- Tight coupling between adapter logic and library-specific interaction objects could complicate framework migrations.
  Mitigation: Isolate all discord.py types and interaction objects within the adapter package behind bridge interfaces to insulate core domain logic.
  Owner: engineering team
- Upstream library breaking changes across major revisions could disrupt gateway connectivity or interaction component contracts.
  Mitigation: Adhere strictly to lock-file version resolution policies and monitor upstream release notes before upgrading library dependencies.
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
- Maintain strict isolation between Discord UI elements such as views, selects, and modals and core domain service clients by delegating via bridge handlers
- Ensure all interaction responses acknowledge user actions within platform latency limits to prevent expired interaction tokens
- Structure slash commands within centralized command routers and register handlers asynchronously during client startup hooks

## Continuation Context


Verify commands:
- Discover and execute the repository unit and integration test runners targeting the Discord adapter module suite
- Discover and run the repository static analysis and linting tools to confirm compliant import usage and rule adherence across all adapter components

Accept when:
- All adapter test suites validate that Discord command routing and view interactions adhere to framework component patterns without unhandled gateway exceptions
- Static dependency analysis confirms no direct references to alternative Discord client libraries exist within the adapter codebase
- Interactive views and background task loops cleanly initialize and shutdown without leaking unclosed event loop resources

## Enforcement

- Verified by: Automated test suites executing interaction handlers and UI views against mocked Discord client fixtures
- Verified by: Continuous integration linters inspecting module imports and verifying compliance with adapter architectural boundaries
- Verified by: Peer code review verifying separation between Discord UI adapters and business logic bridge handlers
- Violation handling: Pull requests introducing direct HTTP Discord requests or bypassing interaction models will be blocked by automated reviews
- Violation handling: Non-compliant command structures must be refactored into designated command routers and UI view classes prior to merging
- Exception process: Submit an architectural change request detailing platform limitations preventing the use of standard discord.py interaction models
- Exception process: Obtain approval from the adapter architecture owner before implementing custom gateway communications
- Exception process: Document all exceptions and maintain isolation within dedicated platform compatibility modules