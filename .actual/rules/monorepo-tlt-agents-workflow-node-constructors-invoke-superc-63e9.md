# BaseNode Contract Adoption for Agent Workflow Execution: Workflow Node Constructors Invoke Superclass Initialization

These rules are ALWAYS ACTIVE for implementation of execution steps and processing nodes within the ambient event agent pipeline, and components performing state transitions, lifecycle tracking, and external service communication inside agent workflows.

### Rules

- **R-BASENODE-001** MUST: Workflow node constructors MUST invoke superclass initialization with an explicit string identifier representing the node name.

### Verify

```bash
# Discover the configured test runner from project metadata and execute the test suite validating BaseNode contract compliance and execute coroutine behavior.
# Locate the repository type verification configuration and run type checking to verify that all node execute implementations conform to the AgentState input and return signatures.
# Discover the linting and static analysis tool from project configuration and verify that all workflow node classes subclass BaseNode and invoke superclass initialization.
```

**Accept when:**
- All workflow node implementations inherit from BaseNode and successfully execute state transformation unit tests without unhandled exceptions.
- Static type analysis confirms that all execute coroutines strictly accept and return AgentState.
- Integration tests confirm that execution steps record state metadata transitions and error statuses under simulated failure conditions.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>