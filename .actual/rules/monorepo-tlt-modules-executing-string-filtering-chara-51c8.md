# Precompiled Regular Expression Pattern Matching with the re Module: Modules Executing String Filtering Character Range

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MOD-001** MUST: Modules executing string filtering, character range validation, or identifier redaction MUST utilize the re module with precompiled pattern objects instantiated via re.compile.

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