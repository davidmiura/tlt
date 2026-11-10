---
version: 2
name: bf71766c-64d6-4495-bdde-f582deb5a487-pil-library-adoption-for-raster-image-processing-and-rendering-before-writing-code-that-uses-versioned
description: "PIL Library Adoption for Raster Image Processing and Rendering: Before Writing Code That Uses Versioned"
metadata:
  actual:
    adr_id: bf71766c-64d6-4495-bdde-f582deb5a487
    status: accepted
    candidate_group_id: ce82a5d0-75ec-40cc-a48d-b3b81e0fe789
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/mcp_services/vibe_bit/**
      - tlt/scripts/**
---

# PIL Library Adoption for Raster Image Processing and Rendering: Before Writing Code That Uses Versioned

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Scope Paths

Root: `monorepo`

Applies to:
- `tlt/mcp_services/vibe_bit/**`
- `tlt/scripts/**`

## Context

- Service and utility components require programmatic raster image manipulation capabilities, including image decoding, drawing overlays, and pixel redaction.
- Inspection of image processing components identifies repeated adoption of PIL for raster image operations across rendering and redaction workflows.
- A standardized imaging abstraction is necessary to ensure consistent memory management and buffer operations across services.

## Problem Statement

Raster image manipulation and rendering across services require a consistent, in-process library abstraction to prevent divergent graphics implementations, redundant decoding logic, and inconsistent buffer handling.

## Decision

1. MUST: Before writing code that uses versioned imaging dependencies, the consumer MUST inspect the repository lock artifact to determine the exact resolved library version and verify API compatibility against documentation for that exact version.

## Policy Block

- MUST Before writing code that uses versioned imaging dependencies, the consumer MUST inspect the repository lock artifact to determine the exact resolved library version and verify API compatibility against documentation for that exact version.

In scope:
- All components, services, and utility scripts performing raster image manipulation, in-memory decoding, programmatic drawing, or image redaction.

Out of scope:
- Components handling non-raster vector definitions without rendering to pixel buffers.
- Text-only processing workflows that do not operate on image pixel data.

## Rationale

- Adopting PIL across rendering and redaction modules provides unified abstractions for raster decoding and geometric drawing.
- Using Image.open with in-memory byte buffers decouples image loading from physical filesystem storage.
- Centralizing on a single imaging library avoids conflicting graphics dependencies and simplifies runtime environment configuration.

## Consequences

Positive:
- Standardizes in-memory raster image decoding, inspection, and manipulation across service and script boundaries.
- Enables programmatic drawing and pixel redaction using established library abstractions.
- Eliminates fragmented custom graphics implementations across rendering and text redaction components.

Negative:
- Raster manipulation operations consume system memory proportionally to image dimensions and pixel depth during in-memory decoding.
- Image rendering and redaction routines execute synchronously within application processes unless explicitly offloaded to background execution pools.
- Dependency surface area includes binary extensions required for raster decoding and manipulation.

## Alternatives

- Direct custom raster byte-array manipulation without a dedicated imaging library (rejected)
  Rejected because: Introduces high implementation complexity, lack of standard format decoders, and substantial maintenance burden for basic drawing and manipulation operations.
  When valid: Applicable only when operating in severely constrained embedded environments where external libraries cannot be packaged.
- Delegation of raster operations to external command-line image processing binaries (rejected)
  Rejected because: Introduces out-of-process execution overhead, inter-process communication serialization costs, and external runtime system dependencies.
  When valid: Applicable when performing batch transformations on formats unsupported by in-process libraries or requiring specialized color-management pipelines.

## Risks

- Decoding excessively large or malformed image buffers may cause high memory allocation or process resource exhaustion.
  Mitigation: Enforce dimension boundaries and validate byte buffer sizes before initiating image decoding.
  Owner: engineering team
- API variations across library revisions may cause runtime failures in drawing or format encoding contracts.
  Mitigation: Verify the exact resolved version in the project resolution artifact and confirm API stability against official documentation.
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
- Encapsulate in-memory byte stream conversions within dedicated adapter functions to isolate buffer handling from core domain logic.
- Ensure all drawing operations instantiate clean drawing contexts and properly scope mutations to local image instances.

## Continuation Context


Verify commands:
- Discover and execute the project test runner to validate that image rendering and redaction test suites pass.
- Discover and execute repository linting and static analysis scripts to verify adherence to approved library import boundaries.

Accept when:
- Image manipulation routines execute without unhandled exceptions across all standard processing pipelines.
- In-memory image decoding and raster drawing operations pass all automated test suites.
- Static analysis verifies that image processing logic adheres to standardized library contracts without undeclared external image dependencies.

## Enforcement

- Verified by: Automated continuous integration checks validating library import constraints and dependency manifests.
- Verified by: Static code analysis rules enforcing approved imaging API contracts.
- Verified by: Peer code review of image processing pipelines.
- Violation handling: Pull requests introducing alternative or unapproved raster processing libraries without an approved exception are blocked.
- Violation handling: Flagged violations must refactor image manipulation logic to conform to standardized PIL interfaces.
- Exception process: Submit an architectural review request detailing technical constraints preventing compliance with the standard imaging library.
- Exception process: Obtain approval from the technical architecture lead prior to introducing alternative imaging abstractions.