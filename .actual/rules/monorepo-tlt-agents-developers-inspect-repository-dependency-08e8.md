# BaseNode Architecture for Ambient Event Agent Nodes: Developers Inspect Repository Dependency Manifest Authoritative

These rules are ALWAYS ACTIVE for all discrete workflow steps, event handlers, and interface processors within the agent node subsystem, and components responsible for asynchronous agent state inspection, transformation, or lifecycle progression.

### Rules

- **R-BASENODE-001** MUST: Developers MUST inspect the repository dependency manifest and authoritative lock artifact to verify all external runtime dependencies match their pinned resolved versions prior to implementing node logic.

### Verify

```bash
# Discover the project verification runner from the repository configuration and execute the automated test suite targeting agent node behaviors.
# Execute the repository linter and static type analyzer according to the project configuration to verify compliance with BaseNode interfaces and AgentState type signatures.
```

**Accept when:**
- All agent workflow nodes inherit from the BaseNode base class and implement the asynchronous execute signature.
- Execution steps, error recovery, and status transitions conform to the BaseNode lifecycle interface without uncaught exceptions escaping the execution boundary.
- Repository verification commands and static analysis suites pass without type or contract violations.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory.
</enforcement>