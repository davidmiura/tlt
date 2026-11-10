---
version: 2
name: cross-cutting-dashboard-web-application-adopt-next-af3e
description: "Adoption of next as Core Application Framework and next/font/google for Font Optimization: Dashboard Web Application Adopt Next Its"
metadata:
  actual:
    adr_id: af3ecb6d-a56a-4719-8039-dd2cb60cf630
    status: accepted
    candidate_group_id: 88544bb8-3f90-46ed-9ef3-09cb57eecaef
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/nextjs_app/dashboard/**
---

# Adoption of next as Core Application Framework and next/font/google for Font Optimization: Dashboard Web Application Adopt Next Its

Scope: applies to `monorepo/tlt/nextjs_app/dashboard/**`.

These rules are ALWAYS ACTIVE for dashboard web applications within the monorepo workspace requiring layout structuring, configuration, and font integration.

### Rules

- **R-FRAMEWORK-001** MUST: The dashboard web application MUST adopt next as its foundational application framework for configuration and page layout structuring.

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