# BaseNode Architecture for Ambient Event Agent Nodes: Workflow Execution Components Within Agent Subsystems

These rules are ALWAYS ACTIVE for all workflow execution components, event handlers, interface processors, and asynchronous agent state transformation steps within agent subsystems.

### Rules

- **R-AGENT-001** MUST: All workflow execution components within agent subsystems MUST subclass BaseNode and implement the asynchronous execute contract accepting and returning AgentState.
- **R-AGENT-002** MUST: Derived node constructors MUST initialize the base class with a distinct, descriptive component identifier string.
- **R-AGENT-003** MUST: State transformations MUST preserve immutable dictionary keys and update progress status through base class helper methods.
- **R-AGENT-004** MUST: External network and messaging operations MUST yield execution asynchronously without blocking the event loop.

### Verify

```bash
# Discover and execute the project verification runner targeting agent node behaviors
# Execute the repository linter and static type analyzer according to project configuration
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull request checks, static type analysis, and peer code reviews enforce BaseNode inheritance and adherence to the AgentState signature.
</enforcement>