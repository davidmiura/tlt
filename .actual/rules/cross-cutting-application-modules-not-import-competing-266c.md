---
version: 2
name: cross-cutting-application-modules-not-import-competing-266c
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Application Modules Not Import Competing Frameworks"
metadata:
  actual:
    adr_id: 266cea5c-42ae-4897-86c8-10ba544c969d
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Application Modules Not Import Competing Frameworks

Scope: applies to `monorepo/tlt/nextjs_app/dashboard/**`.

These rules are ALWAYS ACTIVE for dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

### Rules

- **R-ADR-001** MUST_NOT: Application modules MUST NOT import competing application frameworks or duplicate font orchestration mechanisms within the dashboard scope.

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
Claude Code MUST NOT skip or defer verification. Automated continuous integration and static analysis checks validate dependency manifests, framework imports, and layout module structures.
</enforcement>