---
version: 2
name: cross-cutting-memory-image-loading-raw-byte-3d62
description: "PIL Library Adoption for Raster Image Processing and Rendering: Memory Image Loading Raw Byte Streams"
metadata:
  actual:
    adr_id: 3d62a5ed-c345-4134-a5eb-394e7f705a48
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

# PIL Library Adoption for Raster Image Processing and Rendering: Memory Image Loading Raw Byte Streams

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PIL-001** MUST: In-memory image loading from raw byte streams MUST decode buffers using Image.open with appropriate byte buffer abstractions.

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