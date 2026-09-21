# BaseNode Architecture for Ambient Event Agent Nodes: Node Implementations Record Step Transitions Status

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, and interface processors within the agent node subsystem.

### Rules

- **R-NODE-001** MUST: Node implementations MUST record step transitions and status updates using update_state_metadata rather than directly overwriting root status properties without lifecycle tracking.

### Verify

```bash
# Discover and execute project verification runner targeting agent node behaviors
# Execute repository linter and static type analyzer
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via automated continuous integration test suites, static type analysis, and mandatory peer code reviews.
</enforcement>