---
version: 2
name: 266cea5c-42ae-4897-86c8-10ba544c969d-adoption-of-next-as-core-application-framework-and-next-font-google-for-font-optimization-application-modules-not-import-competing-frameworks
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Application Modules Not Import Competing Frameworks"
metadata:
  actual:
    adr_id: 266cea5c-42ae-4897-86c8-10ba544c969d
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Application Modules Not Import Competing Frameworks

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/nextjs_app/dashboard/**`

## Context

- The dashboard web application requires a standardized application framework to manage UI layouts, routing, and runtime configuration within the workspace.
- Evidence confirms the direct adoption of the next framework across application configuration and root layout structure.
- Root layout composition adopts framework-provided font loading modules to manage typography and global styles consistently.

## Problem Statement

Without a centralized application framework and standard layout architecture, frontend applications risk fragmented build configurations, inconsistent routing structures, and uncoordinated asset loading mechanisms.

## Decision

1. MUST_NOT: Application modules MUST NOT import competing application frameworks or duplicate font orchestration mechanisms within the dashboard scope.

## Policy Block

- MUST_NOT Application modules MUST NOT import competing application frameworks or duplicate font orchestration mechanisms within the dashboard scope.

In scope:
- Dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

Out of scope:
- Non-web packages, backend service workers, and standalone utility libraries in the monorepo that do not render user interfaces.

## Rationale

- Adopting the next framework centralizes application layout definition and build configuration under an established, cohesive architectural model.
- Utilizing the next/font/google utility integrates font optimization directly into layout rendering, minimizing font layout shifts and external asset requests.
- Enforcing a single framework architecture within the dashboard application prevents configuration drift and divergent dependency chains across workspace packages.

## Consequences

Positive:
- Establishes a unified web application architecture providing standard routing, layout nesting, and framework configuration across the application.
- Eliminates redundant asset loading logic by utilizing framework-provided font optimization primitives.
- Standardizes the application runtime boundary within the monorepo workspace.

Negative:
- Couples the dashboard application runtime, layout hierarchy, and build lifecycle to the lifecycle and release cadence of the framework.
- Imposes strict conventions on configuration, layout file structures, and font loading modules that must be learned and maintained.
- Upgrading across major framework versions requires continuous alignment of configuration schemas and component APIs.

## Alternatives

- Independent single-page client rendering library with custom build and routing configuration (rejected)
  Rejected because: Requires assembling and maintaining disparate build pipelines, client routing libraries, and manual font and asset loading pipelines, increasing long-term maintenance overhead.
  When valid: When building lightweight standalone embedded widgets or micro-frontends where server execution and framework runtime footprints are strictly prohibited.
- Traditional multi-page server rendering architecture without integrated client hydrations or font optimization primitives (rejected)
  Rejected because: Lacks first-party primitives for client component hydration, optimized font streaming, and modular application layout composition.
  When valid: When rendering purely static server-generated hypermedia documents without dynamic client-side interactions.

## Risks

- Upstream breaking changes across framework major versions could disrupt layout rendering or configuration parsing.
  Mitigation: Maintain locked dependency versions and enforce automated compatibility tests prior to framework upgrades.
  Owner: engineering team
- Tight coupling to proprietary font optimization modules could complicate migration should alternate font distribution strategies be required.
  Mitigation: Encapsulate framework-specific font calls within root layout modules, maintaining standard CSS token bindings across components.
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
- Ensure the framework configuration module defines valid workspace runtime settings compatible with the monorepo architecture.
- Structure layout hierarchies using framework-provided composition conventions to isolate global styles and typography definitions at the root level.

## Continuation Context


Verify commands:
- Discover and run the project dependency validation script to confirm lockfile integrity and framework version resolution.
- Discover and run the project typecheck and lint scripts to verify framework configuration and layout import compliance.
- Discover and run the project build script to ensure successful framework compilation and asset optimization.

Accept when:
- The application manifest declares the framework dependency and resolves cleanly against the repository lock artifact.
- The framework configuration module and root layout conform to the framework specification without unhandled compilation or runtime errors.
- Static analysis and linting passes confirm all font and layout imports resolve through the framework package namespace without missing peer dependencies.

## Enforcement

- Verified by: Automated continuous integration checks validating dependency manifests against repository lock artifacts.
- Verified by: Static analysis and lint checks verifying framework imports and layout module structures during automated review pipelines.
- Violation handling: Pull requests introducing conflicting application frameworks or unauthorized asset loaders are blocked by automated continuous integration gates.
- Violation handling: Code review must reject any manual bypass of root layout and configuration specifications.
- Exception process: Engineers seeking an alternative application framework or bypassing framework layout conventions must submit an architectural exception proposal to the architecture review board detailing technical justification.
- Exception process: Approved exceptions must document explicit boundaries and maintenance ownership in an architectural override register.