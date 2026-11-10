---
version: 2
name: cross-cutting-components-performing-process-raster-ima-43ec
description: "PIL Library Adoption for Raster Image Processing and Rendering: Components Performing Process Raster Image Decoding"
metadata:
  actual:
    adr_id: 43ec8c14-d29a-49d0-8b2e-e9976df2f2f5
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

# PIL Library Adoption for Raster Image Processing and Rendering: Components Performing Process Raster Image Decoding

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all components, services, and utility scripts performing raster image manipulation, in-memory decoding, programmatic drawing, or image redaction.

### Rules

- **R-PIL-001** MUST: Components performing in-process raster image decoding, manipulation, or rendering MUST use the PIL library for core image operations.

### Verify

\`\`\`bash
# Discover and execute the project test runner to validate that image rendering and redaction test suites pass.
# Discover and execute repository linting and static analysis scripts to verify adherence to approved library import boundaries.
\`\`\`

**Accept when:**
- Image manipulation routines execute without unhandled exceptions across all standard processing pipelines.
- In-memory image decoding and raster drawing operations pass all automated test suites.
- Static analysis verifies that image processing logic adheres to standardized library contracts without undeclared external image dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated continuous integration checks validate library import constraints and dependency manifests, and violations will block pull requests.
</enforcement>