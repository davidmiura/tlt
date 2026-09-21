# Utility Class Layout and CSS Variable Typography Theming: When Utilizing External Presentation Libraries Framework

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- A frontend presentation entry component uses inline utility styling classes to structure layout grids, flex containers, and responsive padding.
- Typography tokens are bound to custom CSS font variables representing sans and mono font families directly in component markup.
- The implementation coexists with an image rendering component from the application framework for media display.
- Static analysis detected these styling tokens across only a single file, indicating localized starter template code rather than a repository-wide design system.

## Problem Statement

Frontend user interfaces require structured layout, spacing, and typography rules, but introducing arbitrary inline utility classes and direct font variable references without centralized component primitives risks visual inconsistency across application modules.

## Decision

1. MUST: When utilizing external presentation libraries or framework components, developers MUST inspect the repository lock artifact to verify the exact resolved version before implementation.

## Policy Block

- MUST When utilizing external presentation libraries or framework components, developers MUST inspect the repository lock artifact to verify the exact resolved version before implementation.

In scope:
- User interface presentation components and layout templates authoring visual styles.

Out of scope:
- Backend services, data fetching routines, and non-visual utility functions.

Exceptions:
- EXC-53-001: Isolated proof-of-concept prototypes or landing page templates that require bespoke presentation before design system extraction.

## Rationale

- The detected pattern shows utility classes specifying layout grids, responsive modifiers, and font family bindings within a single component.
- Centralizing styling tokens and theme variables into established design system primitives prevents styling drift and simplifies maintainability across multiple modules.
- Governing external component libraries against resolved lock versions ensures visual behavior matches documented upstream specifications.

## Consequences

Positive:
- Eliminates visual divergence by constraining layout and typography to governed tokens.
- Improves component readability and maintainability by decoupling markup structure from low-level styling values.
- Ensures consistent responsive behavior and theme switching across application boundaries.

Negative:
- Requires upfront development time to extract reusable component primitives from inline styles.
- Reduces rapid prototyping velocity when implementing custom one-off visual arrangements.

## Alternatives

- Unconstrained ad-hoc utility class authoring across all application components (rejected)
  Rejected because: Leads to styling duplication, divergent visual tokens, and high maintenance overhead across growing frontends
  When valid: Throwaway prototypes or initial scaffold templates prior to architecture establishment
- Dedicated CSS stylesheet modules per component (rejected)
  Rejected because: Fragments token governance and requires maintaining separate styling assets alongside presentation components
  When valid: Component structures requiring legacy stylesheet compatibility or strict style isolation without utility class compilation

## Risks

- Design system component fragmentation if developers continue copying boilerplate utility classes.
  Mitigation: Implement static analysis checks and pull request reviews to enforce design token adoption.
  Owner: Frontend Engineering Team
- Font token mismatches when theme CSS variables are renamed or unconfigured.
  Mitigation: Define and validate typography tokens in a centralized theme schema.
  Owner: Design Systems Team

## Implementation Notes

- DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.

LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
2. Identify the build tool from the manifest.
3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.
- Locate the theme token definitions and font configuration in the repository to bind layout primitives to declared typography variables.
- Extract repetitive grid and flex layout structures into shared presentation components to ensure consistent responsive styling.

## Continuation Context


Verify commands:
- find . -maxdepth 2 -type f | while read -r path; do grep -q "className=" "$path" 2>/dev/null && echo "Inspecting: $path"; done
- test -n "$(grep -rn "font-\[family-name" . 2>/dev/null | head -n 1)" && echo "Detected font variable usage" || echo "No font variables detected"

Accept when:
- Layouts and typography tokens conform to design system primitives verified by the repository validation suite.
- Resolved component library versions in the dependency lock artifact match the active runtime environment.

## Enforcement

- Verified by: Automated linting and static analysis within the continuous integration pipeline.
- Verified by: Peer code review during pull request evaluation.
- Violation handling: Pull requests introducing unapproved ad-hoc styling tokens or unverified component versions are blocked from merging.
- Violation handling: Non-conforming inline styling is flagged for refactoring into reusable design primitives.
- Exception process: Submit an exception request detailing the visual requirement and architectural rationale to the frontend lead.
- Exception process: Approved exceptions must be tracked with a remediation issue for future design system extraction.