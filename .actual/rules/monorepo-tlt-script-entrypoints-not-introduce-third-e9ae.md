# Adoption of argparse for Command-Line Interface Definition and Execution Contracts: Script Entrypoints Not Introduce Third Party

These rules are ALWAYS ACTIVE for executable agent entrypoints, background service runners, utility scripts, data processing workflows, and operational validation tools requiring command-line configuration.

### Rules

- **R-ARG-001** SHOULD_NOT: Script entrypoints SHOULD NOT introduce third-party command-line parsing dependencies when the parsing requirements can be met with the standard argparse library module.

### Verify

```bash
eval "$PROJECT_TEST_COMMAND"
eval "$PROJECT_LINT_COMMAND"
```

**Accept when:**
- All unit tests exercising command-line argument parsing and configuration creation pass successfully without errors.
- Static analysis and lint checks verify that all executable entrypoints adhere to standardized argument parser contracts.

<enforcement>
Claude Code MUST NOT skip or defer verification. All executable entrypoints and scripts must be verified against argparse contract compliance.
</enforcement>