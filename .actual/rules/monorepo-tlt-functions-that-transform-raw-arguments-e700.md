# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Functions That Transform Raw Arguments Structured

These rules are ALWAYS ACTIVE for all executable agent entrypoints, background service runners requiring command-line configuration, utility scripts, data processing workflows, and operational validation tools executed via command line.

### Rules

- **R-ARG-001** MUST: Functions that transform raw arguments into structured application configuration MUST isolate the argument parser definition within a dedicated contract function to facilitate automated testing without invoking runtime side effects.

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