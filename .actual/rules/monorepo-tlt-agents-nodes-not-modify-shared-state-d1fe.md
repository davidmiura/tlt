# BaseNode Contract Adoption for Agent Workflow Execution: Nodes Not Modify Shared State Attributes

These rules are ALWAYS ACTIVE for all implementation of execution steps and processing nodes within the ambient event agent pipeline, and components performing state transitions, lifecycle tracking, and external service communication inside agent workflows.

### Rules

- **R-BASENODE-001** MUST_NOT: Nodes MUST_NOT modify shared state attributes outside the defined execution contract or bypass BaseNode lifecycle logging methods.

### Verify

```bash
# Discover the configured test runner from project metadata and execute test suite validating BaseNode contract compliance
# Locate repository type verification configuration and run type checking
# Discover linting and static analysis tool from project configuration and verify node classes subclass BaseNode
```

**Accept when:**
- All workflow node implementations inherit from BaseNode and successfully execute state transformation unit tests without unhandled exceptions.
- Static type analysis confirms that all execute coroutines strictly accept and return AgentState.
- Integration tests confirm that execution steps record state metadata transitions and error statuses under simulated failure conditions.

<enforcement>
Claude Code MUST NOT skip or defer verification. All workflow nodes must strictly adhere to the BaseNode contract, with verification enforced via automated CI checks and peer code review.
</enforcement>