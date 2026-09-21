# Precompiled Regular Expression Pattern Matching with the re Module: Redaction Utilities Utilize Match Object Methods

These rules are ALWAYS ACTIVE for event adapter components, administrative scripts, and data processing utilities performing character validation, content filtering, message moderation, identifier redaction, token masking, or text sanitization.

### Rules

- **R-RE-001** MAY: Redaction utilities MAY utilize match object methods to perform targeted group extraction and placeholder replacement.
- **R-RE-002** MANDATORY: Instantiate precompiled regular expression objects at module or class scope during initialization rather than inside event loop handlers or per-message callbacks.
- **R-RE-003** MANDATORY: Utilize anchored boundaries when defining identifier patterns to prevent unintended partial substring replacements during sanitization.

### Verify

```bash
# Discover the project test runner through the repository manifest configuration and execute test suites targeting moderation adapters and redaction utilities.
# Discover and execute the repository static analysis tooling to verify that regular expression operations do not execute dynamic uncompiled pattern calls in event loops.
```

**Accept when:**
- All pattern matching operations in event adapters and redaction utilities utilize precompiled regular expression objects instantiated at initialization scope.
- Automated test suites covering message content filtering and sensitive identifier redaction pass without regressions.
- Pattern matching verification confirms that non-conforming message payloads and sensitive credentials are accurately identified without catastrophic backtracking.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated static analysis checks in CI pipelines and peer code reviews.
</enforcement>