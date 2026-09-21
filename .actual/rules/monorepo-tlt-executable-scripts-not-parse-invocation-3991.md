# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Executable Scripts Not Parse Invocation Parameters

These rules are ALWAYS ACTIVE for all executable agent entrypoints, background service runners, utility scripts, data processing workflows, and operational validation tools requiring command-line configuration.

### Rules

- **R-ARG-001** MUST_NOT: Executable scripts MUST NOT parse invocation parameters using manual index-based slice access on system argument lists.

### Verify

```bash
eval "$PROJECT_TEST_COMMAND"
eval "$PROJECT_LINT_COMMAND"
```

**Accept when:**
- All unit tests exercising command-line argument parsing and configuration creation pass successfully without errors.
- Static analysis and lint checks verify that all executable entrypoints adhere to standardized argument parser contracts.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>