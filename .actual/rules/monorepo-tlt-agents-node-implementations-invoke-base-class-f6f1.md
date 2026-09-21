# BaseNode Architecture for Ambient Event Agent Nodes: Node Implementations Invoke Base Class Constructor

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, and interface processors within the agent node subsystem.

### Rules

- **R-BASENODE-001** MUST: Node implementations MUST invoke the base class constructor with a unique component identifier string during initialization.

### Verify

```bash
# Discover and run the project verification runner targeting agent node behaviors
# Run the repository linter and static type analyzer according to project configuration
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated pull request checks and static analysis will reject code that introduces workflow nodes bypassing BaseNode or omitting execute implementations.
</enforcement>