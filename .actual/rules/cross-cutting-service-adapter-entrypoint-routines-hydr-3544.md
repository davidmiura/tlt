---
version: 2
name: cross-cutting-service-adapter-entrypoint-routines-hydr-3544
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Service Adapter Entrypoint Routines Hydrate Process"
metadata:
  actual:
    adr_id: 3544c991-f4ce-4078-ba01-0671591169e3
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

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Service Adapter Entrypoint Routines Hydrate Process

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all microservices, client adapters, gateway proxies, and background agent nodes within the distributed runtime.

### Rules

- **R-ENV-001** SHOULD: Service and adapter entrypoint routines SHOULD hydrate process environment variables from environment configuration files prior to module instantiation using environment file loading routines.
- **R-ENV-002** MANDATORY: Execute environment file hydration calls at the earliest entrypoint phase before importing modules that depend on runtime configuration.
- **R-ENV-003** MANDATORY: Wrap directory paths retrieved from environment variables in standard filesystem path objects rather than performing raw string operations.

### Verify

```bash
# Discover and execute repository static analysis and configuration verification scripts
# Example discovery pattern:
if [ -f "package.json" ]; then
  npm test -- --grep "environment|config"
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  pytest -k "env or config"
fi

# Run test suite with environment variables unset to confirm fallback behavior and fail-fast for secrets
env -u DATABASE_URL -u API_KEY -u SECRET_KEY pytest

# Verify dependency manifests and lock artifacts match locked versions
if [ -f "poetry.lock" ]; then
  poetry check
elif [ -f "package-lock.json" ]; then
  npm ci
fi
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>