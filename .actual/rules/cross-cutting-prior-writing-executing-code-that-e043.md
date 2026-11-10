---
version: 2
name: cross-cutting-prior-writing-executing-code-that-e043
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Prior Writing Executing Code That Consumes"
metadata:
  actual:
    adr_id: e043438e-ae2f-4bca-b719-83e1ff4d133c
    status: accepted
    candidate_group_id: e6112258-c53a-4433-a89b-4d7fee142324
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/adapters/discord_adapter/**
      - tlt/agents/ambient_event_agent/**
      - tlt/mcp_services/**
      - tlt/services/tlt_service/**
---

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Prior Writing Executing Code That Consumes

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ENV-001** MUST: Prior to writing or executing code that consumes versioned external libraries or configuration modules, the consumer MUST inspect the repository lock artifact to determine the exact resolved dependency version and verify API compatibility against version documentation.
- **R-ENV-002** MUST: Execute environment file hydration calls at the earliest entrypoint phase before importing modules that depend on runtime configuration.
- **R-ENV-003** MUST: Wrap directory paths retrieved from environment variables in standard filesystem path objects rather than performing raw string operations.

### Verify

```bash
# Discover and execute static analysis and configuration verification scripts
if [ -f "scripts/verify_config.sh" ]; then
  ./scripts/verify_config.sh
else
  echo "No explicit verify_config.sh found; running dependency and env verification checks"
fi

# Run test suite with environment variables unset to confirm fallback behavior and fail-fast on secrets
ENV_TEST_ISOLATION=1 pytest -v

# Verify dependency manifest and lock artifact sync
if [ -f "requirements.lock" ]; then
  echo "Lock file present"
elif [ -f "poetry.lock" ]; then
  poetry check
else
  echo "Checking lock artifacts..."
fi
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis and test validation gates apply to all changes.
</enforcement>