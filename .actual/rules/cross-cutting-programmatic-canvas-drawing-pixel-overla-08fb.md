---
version: 2
name: cross-cutting-programmatic-canvas-drawing-pixel-overla-08fb
description: "PIL Library Adoption for Raster Image Processing and Rendering: Programmatic Canvas Drawing Pixel Overlay Modifications"
metadata:
  actual:
    adr_id: 08fb96f5-d3da-4b49-b458-895f7517f5d6
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

# PIL Library Adoption for Raster Image Processing and Rendering: Programmatic Canvas Drawing Pixel Overlay Modifications

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all components, services, and utility scripts performing raster image manipulation, in-memory decoding, programmatic drawing, or image redaction.

### Rules

- **R-PIL-001** MUST: Programmatic canvas drawing and pixel overlay modifications MUST use ImageDraw.Draw contexts created from active image instances.

### Verify

```bash
# Discover and execute the project test runner to validate that image rendering and redaction test suites pass.
# Discover and execute repository linting and static analysis scripts to verify adherence to approved library import boundaries.
```

**Accept when:**
- Image manipulation routines execute without unhandled exceptions across all standard processing pipelines.
- In-memory image decoding and raster drawing operations pass all automated test suites.
- Static analysis verifies that image processing logic adheres to standardized library contracts without undeclared external image dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>