# Adoption of PIL for Image Processing and Canvas Rendering: Modules Requiring Raster Image Manipulation Memory

Status: proposed
Date: 2025-05-18
Deciders: Detection Pipeline (automated)

## Context

- Services and automation scripts across the codebase require 2D raster graphic rendering, dynamic canvas compositing, and visual content redaction.
- Handling binary image manipulation natively without a unified abstraction leads to fragmented implementations and potential memory handling defects.
- The codebase establishes PIL as the standard interface for loading, drawing, transforming, and streaming image buffers across application modules.

## Problem Statement

Manipulating image byte streams and applying drawing transformations across services and utility scripts without a standardized library introduces inconsistent memory buffering, inconsistent file format handling, and divergent drawing APIs.

## Decision

1. MUST: Modules requiring raster image manipulation, in-memory image streaming, and drawing transformations MUST standardize on the PIL library.

## Policy Block

- MUST Modules requiring raster image manipulation, in-memory image streaming, and drawing transformations MUST standardize on the PIL library.

In scope:
- Image rendering services generating visual canvases, previews, or multi-frame representations.
- Automation scripts performing visual redaction, transformation, or batch image analysis.

Out of scope:
- Vector graphics generation where scalable format definitions do not map to raster grids.
- Raw byte transmission pipelines that do not decode, inspect, or transform image payloads.

Exceptions:
- EXC-20-001: Specialized computer vision operations require external tensor transformations beyond standard raster manipulation

## Rationale

- Evidence demonstrates consistent utilization of PIL across both service-level canvas rendering contracts and script-based image redaction workflows.
- Standardizing on PIL provides consistent memory-buffered manipulation via Image and ImageDraw interfaces without incurring the overhead of heavy scientific computing suites.
- Centralizing image manipulation around an established core library minimizes operational variance across services and maintenance automation.

## Consequences

Positive:
- Standardized image decoding, drawing primitives, and buffer serialization across backend services and tooling.
- Predictable in-memory byte handling reducing file system serialization overhead.
- Consistent error handling and image lifetime management across asynchronous rendering pipelines.

Negative:
- Synchronous CPU-bound image manipulation within PIL can create latency bottlenecks during heavy rendering loads without asynchronous offloading.
- Additional memory footprint when buffering uncompressed raster frames concurrently.

## Alternatives

- Adopting heavyweight computer vision frameworks for all image processing tasks (rejected)
  Rejected because: Introduces significant dependency overhead, complex native build requirements, and unnecessary abstraction layers for 2D canvas drawing and redaction
  When valid: When advanced feature extraction, multi-dimensional tensor processing, or machine learning model integration is strictly required
- Implementing custom binary image encoders and raw byte manipulation routines (rejected)
  Rejected because: Carries high maintenance cost, heightened risk of buffer management defects, and poor format extensibility
  When valid: When operating in deeply constrained environments where external dependencies cannot be installed

## Risks

- Large raster images decoded in memory concurrently can cause excessive heap consumption
  Mitigation: Enforce dimension limits, streaming bounds, and proper disposal of intermediate image drawing instances
  Owner: Engineering team
- API behavior shifts across major library updates could alter rendering output or byte serialization format
  Mitigation: Strict adherence to repository dependency lock artifacts and automated visual regression test suites
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
- Manage image byte streams via in-memory buffer adapters to ensure image decoders release resources promptly after rendering or redaction.
- Isolate CPU-intensive drawing and redaction routines from blocking event loops in service contexts.

## Continuation Context


Verify commands:
- Discover the repository test runner from the root configuration and execute image rendering test suites.
- Discover the repository static analysis tooling and verify dependency imports against approved library declarations.

Accept when:
- All unit and integration test suites validating image rendering and redaction pass cleanly.
- Static analysis checks report no unauthorized imports or unresolved image manipulation dependencies.

## Enforcement

- Verified by: Automated continuous integration pipeline execution of test suites and static analysis checks.
- Verified by: Peer code review verifying adherence to drawing patterns and memory stream conventions.
- Violation handling: Pull requests introducing divergent image processing libraries or unmanaged native calls will fail automated checks and be blocked from merge.
- Exception process: Formal architectural exception request submitted with benchmarking and justification against standard PIL capabilities.