# Adoption of PIL for Image Processing and Canvas Rendering: Modules Not Invoke Unmanaged Native Graphical

These rules are ALWAYS ACTIVE for all services and automation scripts performing 2D raster graphic rendering, dynamic canvas compositing, and visual content redaction.

### Rules

- **R-PIL-001** MUST_NOT: Modules MUST_NOT invoke unmanaged native graphical subsystems directly when standard PIL image and drawing primitives satisfy functional requirements.

### Verify

```bash
# Discover the repository test runner from the root configuration and execute image rendering test suites.
# Discover the repository static analysis tooling and verify dependency imports against approved library declarations.
```

**Accept when:**
- All unit and integration test suites validating image rendering and redaction pass cleanly.
- Static analysis checks report no unauthorized imports or unresolved image manipulation dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>