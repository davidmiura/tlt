# BaseNode Contract Adoption for Agent Workflow Execution: Nodes Record Lifecycle Progression Through Update

These rules are ALWAYS ACTIVE for all implementation of execution steps and processing nodes within the ambient event agent pipeline, and components performing state transitions, lifecycle tracking, and external service communication inside agent workflows.

### Rules

- **R-BASENODE-001** MUST: Nodes MUST record lifecycle progression through update_state_metadata, setting the status and processing step attributes on AgentState during execution.

### Verify

```bash
# Discover and run test suite validating BaseNode contract compliance and execute coroutine behavior
# Run type checking to verify that all node execute implementations conform to the AgentState input and return signatures
# Run linting and static analysis to verify that all workflow node classes subclass BaseNode and invoke superclass initialization
```

**Accept when:**
- All workflow node implementations inherit from BaseNode and successfully execute state transformation unit tests without unhandled exceptions.
- Static type analysis confirms that all execute coroutines strictly accept and return AgentState.
- Integration tests confirm that execution steps record state metadata transitions and error statuses under simulated failure conditions.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration pipeline and peer review enforce BaseNode contract compliance.
</enforcement>