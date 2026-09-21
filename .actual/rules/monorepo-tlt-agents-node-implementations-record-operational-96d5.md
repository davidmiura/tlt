# BaseNode Architecture for Ambient Event Agent Nodes: Node Implementations Record Operational Milestones Lifecycle

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, and interface processors within the agent node subsystem.

### Rules

- **R-NODES-001** SHOULD: Node implementations SHOULD record operational milestones and lifecycle progress through log_execution to maintain standardized diagnostic tracing.

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
Claude Code MUST NOT skip or defer verification. Automated continuous integration, static type analysis, and mandatory peer code reviews enforce compliance.
</enforcement>