# Precompiled Regular Expression Pattern Matching with the re Module: Before Implementing Updating Pattern Matching Logic

These rules are ALWAYS ACTIVE for event adapter components performing character validation, content filtering, message moderation, administrative scripts, and utilities executing identifier redaction, token masking, or text sanitization.

### Rules

- **R-RE-001** MUST: Before implementing or updating pattern matching logic that interfaces with versioned runtime libraries, consumers MUST inspect the repository lock or resolution artifact to determine the exact resolved version in accordance with the discovery policy.
- **R-RE-002** MUST: Instantiate precompiled regular expression objects at module or class scope during initialization rather than inside event loop handlers or per-message callbacks.
- **R-RE-003** MUST: Utilize anchored boundaries when defining identifier patterns to prevent unintended partial substring replacements during sanitization.

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
Claude Code MUST NOT skip or defer verification. Automated static analysis checks and peer code reviews enforce compliance.
</enforcement>