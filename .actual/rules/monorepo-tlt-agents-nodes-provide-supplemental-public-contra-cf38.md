# BaseNode Contract Adoption for Agent Workflow Execution: Nodes Provide Supplemental Public Contract Methods

These rules are ALWAYS ACTIVE for all implementation steps and processing nodes within the ambient event agent pipeline, and components performing state transitions, lifecycle tracking, and external service communication inside agent workflows.

### Rules

- **R-BASENODE-001** MAY: Nodes MAY provide supplemental public contract methods for immediate or out-of-band operations while maintaining internal rate limit and execution tracking.
- **R-BASENODE-002** MANDATORY: The consumer MUST discover tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-BASENODE-003** MANDATORY: Before writing code that uses a versioned library, execute in order: find the dependency manifest, identify the build tool, inspect the repository lock or resolution artifact to determine the exact resolved version, look up official documentation for that exact version, confirm every API/class/function exists in that version, and re-verify per dependency at point of use for version-sensitive behavior.
- **R-BASENODE-004** MANDATORY: When constructing a new workflow node, ensure the string identifier passed to superclass initialization matches the canonical node designation used in pipeline orchestration configuration.
- **R-BASENODE-005** MANDATORY: Implement rate limiting and scheduling verification inside the node execute loop prior to invoking external network operations or third-party service adapters.
- **R-BASENODE-006** MANDATORY: Verify that state mutations preserve immutable event identifiers and retain existing metadata keys across processing steps.

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
Verification is mandatory. Continuous integration pipeline fails the build when workflow nodes deviate from the BaseNode contract or fail type checks, and pull requests introducing non-compliant workflow steps or bypassed lifecycle methods are blocked from merging.
</enforcement>