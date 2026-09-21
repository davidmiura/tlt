# Utility Class Layout and CSS Variable Typography Theming: When Utilizing External Presentation Libraries Framework

These rules are ALWAYS ACTIVE for user interface presentation components and layout templates authoring visual styles.

### Rules

- **R-UTIL-001** MUST: When utilizing external presentation libraries or framework components, developers MUST inspect the repository lock artifact to verify the exact resolved version before implementation.

### Verify

```bash
find . -maxdepth 2 -type f | while read -r path; do grep -q "className=" "$path" 2>/dev/null && echo "Inspecting: $path"; done
test -n "$(grep -rn "font-\[family-name" . 2>/dev/null | head -n 1)" && echo "Detected font variable usage" || echo "No font variables detected"
```

**Accept when:**
- Layouts and typography tokens conform to design system primitives verified by the repository validation suite.
- Resolved component library versions in the dependency lock artifact match the active runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated linting, static analysis, and peer code review enforce these policies.
</enforcement>