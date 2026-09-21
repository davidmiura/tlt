# Adoption of tlt Internal Namespace Module Architecture: Subsystem Internal Modules Not Establish Circular

These rules are ALWAYS ACTIVE for all internal module authoring, restructuring, and cross-package dependency integration within the monorepo codebase.

### Rules

- **R-TLT-001** MUST_NOT: Subsystem internal modules MUST NOT establish circular import dependencies with external caller packages.

### Verify

```bash
# Discover and run project static analysis, linting, and dependency graph analyzers to verify no circular dependencies exist
```

**Accept when:**
- All internal module imports adhere to absolute paths rooted at the designated namespace package with zero relative cross-boundary imports.
- Static boundary checks and automated verification test suites complete without errors or dependency cycle warnings.
- All shared contracts are consumed from designated shared namespaces without importing private subsystem internals.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration static analysis pipelines and automated boundary checks must run and pass without errors.
</enforcement>