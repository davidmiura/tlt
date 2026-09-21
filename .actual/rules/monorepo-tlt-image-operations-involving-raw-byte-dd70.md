# Adoption of PIL for Image Processing and Canvas Rendering: Image Operations Involving Raw Byte Streams

These rules are ALWAYS ACTIVE for all image rendering services, automation scripts performing visual redaction/transformation, and canvas compositing workflows operating on raw byte streams.

### Rules

- **R-PIL-001** MUST: Image operations involving raw byte streams MUST interact with PIL through memory buffer adapters using Image.open to avoid unnecessary disk input and output operations.

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