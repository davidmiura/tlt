# BaseNode Contract Adoption for Agent Workflow Execution: Agent Workflow Execution Nodes Inherit Basenode

These rules are ALWAYS ACTIVE for all agent workflow node authoring, review, and execution processes.

### Rules

- **R-AN-001** MUST: All agent workflow execution nodes MUST inherit from BaseNode and implement the asynchronous execute method accepting AgentState as input and returning the mutated AgentState.

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
Claude Code MUST NOT skip or defer verification. Continuous integration pipeline fails the build when workflow nodes deviate from the BaseNode contract or fail type checks.
</enforcement>