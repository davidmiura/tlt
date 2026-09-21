# BaseNode Contract Adoption for Agent Workflow Execution: Before Introducing Modifying Dependencies Used Workflow

These rules are ALWAYS ACTIVE for implementation of execution steps, processing nodes, state transitions, lifecycle tracking, and external service communication inside the ambient event agent pipeline.

### Rules

- **R-AGNT-001** MUST: Before introducing or modifying dependencies used by workflow nodes, consumers MUST inspect the repository lock artifact to determine the exact resolved dependency versions.

### Verify

```bash
# Discover and run the configured test runner validating BaseNode contract compliance and execute coroutine behavior
# Locate repository type verification configuration and run type checking for AgentState input/return signatures
# Discover linting and static analysis tool from project configuration to verify workflow node BaseNode subclassing
```

**Accept when:**
- All workflow node implementations inherit from BaseNode and successfully execute state transformation unit tests without unhandled exceptions.
- Static type analysis confirms that all execute coroutines strictly accept and return AgentState.
- Integration tests confirm that execution steps record state metadata transitions and error statuses under simulated failure conditions.

<enforcement>
Verification is mandatory. Claude Code MUST NOT skip or defer verification.
</enforcement>