# Adoption of tlt Internal Namespace Module Architecture: Developers Inspect Repository Dependency Manifest Authoritative

These rules are ALWAYS ACTIVE for all internal module authoring, restructuring, and cross-package dependency integration within the monorepo codebase.

### Rules

- **R-NAMESPACE-001** MUST: Developers MUST inspect the repository dependency manifest and authoritative lock artifact to verify resolved package dependency versions prior to implementing module interfaces.

### Verify

```bash
# Discover and run the project static analysis and linting suite to verify import formatting and boundary constraints.
# Discover and run the project test suite to confirm cross-module integration and contract compatibility.
# Discover and run the dependency graph analyzer to verify that no circular dependencies exist between namespace modules.
```

**Accept when:**
- All internal module imports adhere to absolute paths rooted at the designated namespace package with zero relative cross-boundary imports.
- Static boundary checks and automated verification test suites complete without errors or dependency cycle warnings.
- All shared contracts are consumed from designated shared namespaces without importing private subsystem internals.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by continuous integration static analysis pipelines and peer code reviews.
</enforcement>