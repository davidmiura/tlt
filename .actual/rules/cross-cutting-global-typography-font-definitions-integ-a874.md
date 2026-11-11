---
version: 2
name: cross-cutting-global-typography-font-definitions-integ-a874
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Global Typography Font Definitions Integrated Root"
metadata:
  actual:
    adr_id: a874fb9c-5af6-44e9-b9d5-d41eca81e43f
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Global Typography Font Definitions Integrated Root

Scope: applies to `monorepo/tlt/nextjs_app/dashboard/**`.

These rules are ALWAYS ACTIVE for dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

### Rules

- **R-FRAMEWORK-001** MUST: Global typography and font definitions integrated into root layouts MUST use the framework-provided next/font/google module rather than unmanaged remote stylesheet links.

### Verify

```bash
# Discover and run the project dependency validation script to confirm lockfile integrity and framework version resolution.
# Discover and run the project typecheck and lint scripts to verify framework configuration and layout import compliance.
# Discover and run the project build script to ensure successful framework compilation and asset optimization.
```

**Accept when:**
- The application manifest declares the framework dependency and resolves cleanly against the repository lock artifact.
- The framework configuration module and root layout conform to the framework specification without unhandled compilation or runtime errors.
- Static analysis and linting passes confirm all font and layout imports resolve through the framework package namespace without missing peer dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>