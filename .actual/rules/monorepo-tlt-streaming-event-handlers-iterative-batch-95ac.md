# Precompiled Regular Expression Pattern Matching with the re Module: Streaming Event Handlers Iterative Batch Processing

These rules are ALWAYS ACTIVE for event adapter components performing character validation, content filtering, or message moderation, as well as administrative scripts and utilities executing identifier redaction, token masking, or text sanitization.

### Rules

- **R-STREAM-001** MUST_NOT: Streaming event handlers and iterative batch processing loops MUST NOT invoke uncompiled regular expression functions dynamically within execution hot paths.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>