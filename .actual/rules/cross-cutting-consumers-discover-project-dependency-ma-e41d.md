---
version: 2
name: cross-cutting-consumers-discover-project-dependency-ma-e41d
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Consumers Discover Project Dependency Manifest Lock"
metadata:
  actual:
    adr_id: e41d5988-12b1-48f4-92f2-d88028d68b0a
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Consumers Discover Project Dependency Manifest Lock

Scope: applies to `monorepo/tlt/nextjs_app/dashboard/**`.

These rules are ALWAYS ACTIVE for dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

### Rules

- **R-NEXT-001** MUST: Consumers MUST discover the project dependency manifest and lock resolution artifact to verify the exact resolved framework version prior to implementing or consuming framework APIs.

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
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>