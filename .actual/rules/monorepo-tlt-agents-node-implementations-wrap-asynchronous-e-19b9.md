# BaseNode Architecture for Ambient Event Agent Nodes: Node Implementations Wrap Asynchronous Execution Bodies

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, interface processors, and asynchronous state inspection, transformation, or lifecycle progression components within the agent node subsystem.

### Rules

- **R-BASENODE-001** MUST: Node implementations MUST wrap asynchronous execution bodies in structured exception handling that delegates failure recovery and error state transitions to handle_error.

### Verify

```bash
# Discover and execute the project verification runner targeting agent node behaviors
# Run repository linter and static type analyzer according to project configuration
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>