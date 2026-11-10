---
version: 2
name: cross-cutting-framework-specific-runtime-build-setting-64c9
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Framework Specific Runtime Build Settings Encapsulated"
metadata:
  actual:
    adr_id: 64c9bdeb-10db-417f-a65c-2f282b09e209
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Framework Specific Runtime Build Settings Encapsulated

Scope: applies to `monorepo/tlt/nextjs_app/dashboard/**`.

These rules are ALWAYS ACTIVE for all dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

### Rules

- **R-FWK-001** SHOULD: Framework-specific runtime and build settings SHOULD be encapsulated within the designated framework configuration module at the application root.

### Verify

```bash
# Discover and run project dependency validation, typecheck, lint, and build scripts
# (Repository-specific commands to be resolved from package manifests)
```

**Accept when:**
- The application manifest declares the framework dependency and resolves cleanly against the repository lock artifact.
- The framework configuration module and root layout conform to the framework specification without unhandled compilation or runtime errors.
- Static analysis and linting passes confirm all font and layout imports resolve through the framework package namespace without missing peer dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated continuous integration checks and static analysis verification are mandatory.
</enforcement>