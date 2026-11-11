---
version: 2
name: cross-cutting-image-processing-routines-handle-decodin-1982
description: "PIL Library Adoption for Raster Image Processing and Rendering: Image Processing Routines Handle Decoding Exceptions"
metadata:
  actual:
    adr_id: 1982a70f-db54-4992-8cfe-956f1431fa90
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

# PIL Library Adoption for Raster Image Processing and Rendering: Image Processing Routines Handle Decoding Exceptions

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PIL-001** SHOULD: Image processing routines SHOULD handle image decoding exceptions gracefully and record structured diagnostics when decoding fails.

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