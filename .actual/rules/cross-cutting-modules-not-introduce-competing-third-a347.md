---
version: 2
name: cross-cutting-modules-not-introduce-competing-third-a347
description: "PIL Library Adoption for Raster Image Processing and Rendering: Modules Not Introduce Competing Third Party"
metadata:
  actual:
    adr_id: a3473d9c-fae2-4ceb-a85a-2989a697b6de
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

# PIL Library Adoption for Raster Image Processing and Rendering: Modules Not Introduce Competing Third Party

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-PIL-001** MUST_NOT: Modules MUST NOT introduce competing third-party raster image processing libraries for drawing and redaction operations governed by this decision.

### Verify

```bash
# Discover and execute project test runner and linting/static analysis scripts
# (e.g., pytest, ruff, flake8, or equivalent as defined by project repository)
```

**Accept when:**
- Image manipulation routines execute without unhandled exceptions across all standard processing pipelines.
- In-memory image decoding and raster drawing operations pass all automated test suites.
- Static analysis verifies that image processing logic adheres to standardized library contracts without undeclared external image dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>