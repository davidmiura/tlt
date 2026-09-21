# Adoption of PIL for Image Processing and Canvas Rendering: Before Implementing Image Processing Features Consumer

These rules are ALWAYS ACTIVE for image rendering services, canvas compositing scripts, visual content redaction routines, and automation scripts performing visual transformations.

### Rules

- **R-PIL-001** MUST: Before implementing image processing features, the consumer MUST inspect the repository dependency lock artifact to determine and adhere to the exact resolved library version.

### Verify

```bash
# Discover and execute image rendering test suites and verify static analysis/dependency imports
# (Refer to repository configuration for test runner and static analysis tools)
```

**Accept when:**
- All unit and integration test suites validating image rendering and redaction pass cleanly.
- Static analysis checks report no unauthorized imports or unresolved image manipulation dependencies.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>