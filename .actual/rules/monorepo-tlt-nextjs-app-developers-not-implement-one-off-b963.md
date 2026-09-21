# Utility Class Layout and CSS Variable Typography Theming: Developers Not Implement One Off Arbitrary

These rules are ALWAYS ACTIVE for user interface presentation components and layout templates authoring visual styles.

### Rules

- **R-TLT-001** MUST_NOT: Developers MUST_NOT implement one-off arbitrary dimensions or hardcoded spacing strings directly in component markup without design token validation.

### Verify

```bash
find . -maxdepth 2 -type f | while read -r path; do grep -q "className=" "$path" 2>/dev/null && echo "Inspecting: $path"; done
test -n "$(grep -rn "font-\[family-name" . 2>/dev/null | head -n 1)" && echo "Detected font variable usage" || echo "No font variables detected"
```

**Accept when:**
- Layouts and typography tokens conform to design system primitives verified by the repository validation suite.
- Resolved component library versions in the dependency lock artifact match the active runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>