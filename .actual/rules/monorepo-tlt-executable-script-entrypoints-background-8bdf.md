# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Executable Script Entrypoints Background Agent Runners

These rules are ALWAYS ACTIVE for all executable script entrypoints and background agent runners that accept invocation parameters, as well as utility scripts, data processing workflows, and operational validation tools executed via the command line.

### Rules

- **R-ARG-001** MUST: All executable script entrypoints and background agent runners that accept invocation parameters MUST use argparse to define, parse, and validate command-line arguments.

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