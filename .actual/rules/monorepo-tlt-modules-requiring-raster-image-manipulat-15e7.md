# Adoption of PIL for Image Processing and Canvas Rendering: Modules Requiring Raster Image Manipulation Memory

These rules are ALWAYS ACTIVE for modules requiring raster image manipulation, in-memory image streaming, and drawing transformations.

### Rules

- **R-PIL-001** MUST: Modules requiring raster image manipulation, in-memory image streaming, and drawing transformations MUST standardize on the PIL library.

### Verify

```bash
# Discover the repository test runner from the root configuration and execute image rendering test suites.
# Discover the repository static analysis tooling and verify dependency imports against approved library declarations.
```

**Accept when:**
- All unit and integration test suites validating image rendering and redaction pass cleanly.
- Static analysis checks report no unauthorized imports or unresolved image manipulation dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated continuous integration pipeline execution of test suites, static analysis checks, and peer code review enforce adherence to drawing patterns and memory stream conventions.
</enforcement>