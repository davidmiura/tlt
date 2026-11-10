---
version: 2
name: cross-cutting-before-writing-code-that-uses-bf71
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

Scope: applies to `monorepo/tlt/mcp_services/vibe_bit/**`, `monorepo/tlt/scripts/**`.

These rules are ALWAYS ACTIVE for all components, services, and utility scripts performing raster image manipulation, in-memory decoding, programmatic drawing, or image redaction.

### Rules

- **R-PIL-001** MUST: Before writing code that uses versioned imaging dependencies, the consumer MUST inspect the repository lock artifact to determine the exact resolved library version and verify API compatibility against documentation for that exact version.

### Verify

```bash
# Discover and execute the project test runner and linting scripts
# Example discovery step:
if [ -f "package.json" ]; then
  npm test
  npm run lint
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  pytest
  flake8 || ruff check .
fi
```

**Accept when:**
- Image manipulation routines execute without unhandled exceptions across all standard processing pipelines.
- In-memory image decoding and raster drawing operations pass all automated test suites.
- Static analysis verifies that image processing logic adheres to standardized library contracts without undeclared external image dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>