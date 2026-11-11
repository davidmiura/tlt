---
version: 2
name: cross-cutting-configuration-variables-requiring-numeri-c342
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Configuration Variables Requiring Numeric Boolean Structured"
metadata:
  actual:
    adr_id: c342ec3c-c018-49eb-8573-9190bdcd9dd9
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

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Configuration Variables Requiring Numeric Boolean Structured

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all microservices, client adapters, gateway proxies, and background agent nodes within the distributed runtime.

### Rules

- **R-CFG-001** MUST: Configuration variables requiring numeric, boolean, or structured types MUST perform type casting and format validation immediately upon extraction from string-based environment variables.
- **R-CFG-002** MANDATORY: Execute environment file hydration calls at the earliest entrypoint phase before importing modules that depend on runtime configuration.
- **R-CFG-003** MANDATORY: Wrap directory paths retrieved from environment variables in standard filesystem path objects rather than performing raw string operations.

### Verify

```bash
# Discover and execute the repository static analysis and configuration verification scripts
# Discover and execute the repository test suite with environment variables unset
# Discover the dependency manifest and authoritative lock artifact to verify all declared runtime environment and configuration libraries match exact locked versions
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>