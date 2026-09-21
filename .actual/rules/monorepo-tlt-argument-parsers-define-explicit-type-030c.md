# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Argument Parsers Define Explicit Type Constraints

These rules are ALWAYS ACTIVE for all executable agent entrypoints, background service runners requiring command-line configuration, utility scripts, data processing workflows, and operational validation tools executed via command line.

### Rules

- **R-ARG-001** SHOULD: Argument parsers SHOULD define explicit type constraints, default values, and descriptive help messages for all declared options and flags.

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