# BaseNode Architecture for Ambient Event Agent Nodes: Node Operations Performing External Communication Timed

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, interface processors, and asynchronous agent state inspection, transformation, or lifecycle progression components within the agent node subsystem.

### Rules

- **R-BASENODE-001** MUST_NOT: Node operations performing external communication or timed waiting MUST NOT perform blocking synchronous calls and MUST execute non-blocking asynchronous routines.

### Verify

```bash
# Discover the project verification runner from repository configuration and execute test suite
# Execute repository linter and static type analyzer according to project configuration
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated continuous integration test suites, static type analysis, and mandatory peer code reviews.
</enforcement>