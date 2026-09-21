# Adoption of tlt Internal Namespace Module Architecture: Subsystem Internal Modules Not Establish Circular

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Multiple subsystems including service routers, autonomous agent execution nodes, protocol adapters, and tool gateways coexist within a shared monorepo codebase.
- Subsystems require clear domain isolation while consuming shared data schemas and cross-cutting capabilities across operational boundaries.
- Unstructured imports and ad-hoc relative path resolutions across subsystem boundaries create fragile coupling and circular import hazards.

## Problem Statement

In a multi-component monorepo containing services, agents, protocol adapters, and tool gateways, unregulated module organization leads to tight coupling, fragile relative import chains across subsystem boundaries, and duplicate interface declarations. Without an enforced internal namespace module architecture, developer changes in one subsystem risk inadvertent cross-domain pollution and circular dependency cycles.

## Decision

1. MUST_NOT: Subsystem internal modules MUST NOT establish circular import dependencies with external caller packages.

## Policy Block

- MUST_NOT Subsystem internal modules MUST NOT establish circular import dependencies with external caller packages.

In scope:
- All internal module authoring, restructuring, and cross-package dependency integration within the monorepo codebase.
- Definition and consumption of shared data schemas, service routers, agent workflows, and protocol adapters.

Out of scope:
- Third-party vendor libraries that do not participate in monorepo namespace resolution.
- Isolated single-script utility programs that operate outside repository packaging boundaries.

## Rationale

- Enforcing a root namespace module convention ensures consistent import ergonomics and prevents deep relative path escalation across distinct domain packages.
- Centralizing shared contracts in common namespace packages decouples domain consumers from specific service or adapter implementations.
- The architectural pattern is evidenced across thirty-one monorepo files with ninety percent detection significance, validating standard codebase practice.

## Consequences

Positive:
- Provides deterministic, absolute import resolution across services, agents, adapters, and shared components.
- Eliminates circular dependency traps and fragile directory-relative import statements.
- Encourages decoupled domain architectures by requiring clear contract definition in designated shared namespaces.

Negative:
- Requires longer, fully qualified import paths throughout the codebase.
- Imposes namespace packaging governance when scaffolding new micro-components or utility modules.

## Alternatives

- Relative directory import traversal across domain boundaries (rejected)
  Rejected because: Relative traversals break when files are reorganized, obscure package boundaries, and increase susceptibility to circular import deadlocks.
  When valid: Small single-package projects with flat directory structures and no distinct subsystem boundaries.
- Independent multi-repository distribution for each domain subsystem (rejected)
  Rejected because: Introduces cross-repository version management overhead and slows atomic schema migration across tightly coordinated agent and service nodes.
  When valid: Fully autonomous services managed by separate organizational teams with distinct deployment lifecycles.

## Risks

- Developers bypass shared namespace contracts and import private implementation internals from peer subsystems.
  Mitigation: Automated linting and architecture boundary checks in continuous integration to disallow cross-boundary access to private symbols.
  Owner: engineering team
- Accidental introduction of circular dependencies between shared modules and consuming domain packages.
  Mitigation: Enforce strict dependency layer directionality where shared packages never import from higher-level domain subsystems.
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
- Configure workspace module resolution in project configuration manifests to recognize the root namespace package across all source trees.
- Organize new subsystem capabilities into domain-specific subpackages beneath the root namespace and export stable interfaces through module entrypoints.

## Continuation Context


Verify commands:
- Discover and run the project static analysis and linting suite to verify import formatting and boundary constraints.
- Discover and run the project test suite to confirm cross-module integration and contract compatibility.
- Discover and run the dependency graph analyzer to verify that no circular dependencies exist between namespace modules.

Accept when:
- All internal module imports adhere to absolute paths rooted at the designated namespace package with zero relative cross-boundary imports.
- Static boundary checks and automated verification test suites complete without errors or dependency cycle warnings.
- All shared contracts are consumed from designated shared namespaces without importing private subsystem internals.

## Enforcement

- Verified by: Continuous integration static analysis pipelines that check module boundaries and import paths.
- Verified by: Peer code review verification of architectural boundary adherence.
- Violation handling: Build pipeline failure on invalid cross-boundary imports or circular dependencies.
- Violation handling: Mandatory refactoring of non-compliant import statements prior to merging changes.
- Exception process: Architectural review submission documented in technical request for comments and approved by technical leads.