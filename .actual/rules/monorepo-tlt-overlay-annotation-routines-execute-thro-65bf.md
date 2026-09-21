# Adoption of PIL for Image Processing and Canvas Rendering: Overlay Annotation Routines Execute Through Imagedraw

These rules are ALWAYS ACTIVE for image rendering services generating visual canvases, previews, or multi-frame representations, and automation scripts performing visual redaction, transformation, or batch image analysis.

### Rules

- **R-PIL-001** SHOULD: Overlay and annotation routines SHOULD execute through ImageDraw drawing contexts derived from instantiated image objects.
- **R-PIL-002** MANDATORY: The consumer MUST discover tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-PIL-003** MANDATORY: Before writing code that uses a versioned library, execute in order: find dependency manifest, identify build tool, inspect repository lock or resolution artifact for exact resolved version, look up official documentation for that exact version, confirm every API/class/function exists in that version, and re-run steps 3-5 per dependency at point of use for version-sensitive behavior.

### Verify

```bash
# Discover the repository test runner from the root configuration and execute image rendering test suites.
# Discover the repository static analysis tooling and verify dependency imports against approved library declarations.
```

**Accept when:**
- All unit and integration test suites validating image rendering and redaction pass cleanly.
- Static analysis checks report no unauthorized imports or unresolved image manipulation dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated continuous integration pipeline execution of test suites and static analysis checks, as well as peer code review, verify adherence to drawing patterns and memory stream conventions. Pull requests introducing divergent image processing libraries or unmanaged native calls will fail automated checks and be merged.
</enforcement>