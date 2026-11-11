---
version: 2
name: cross-cutting-every-runtime-configuration-parameter-ne-04a3
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Every Runtime Configuration Parameter Network Service"
metadata:
  actual:
    adr_id: 04a32626-3a6f-41f7-860b-9a7500b38e03
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

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Every Runtime Configuration Parameter Network Service

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all microservices, client adapters, gateway proxies, background agent nodes, and configuration parameters defining network locations, communication ports, filesystem paths, runtime environments, log levels, and authentication secrets.

### Rules

- **R-ENV-001** MUST: Retrieve every runtime configuration parameter, network service endpoint, communication port, and persistence directory through environment variable sourcing functions, specifying explicit local fallback values for operational non-secret parameters.
- **R-ENV-002** MANDATORY (DISCOVERY POLICY): Omit all tool names, file names, commands, package managers, and version numbers in implementations; the consumer MUST derive them from the project repository.
- **R-ENV-003** MANDATORY (LOCK-VERSION GROUNDING): Before writing code that uses a versioned library, execute in order: find the dependency manifest, identify the build tool, inspect the repository lock or resolution artifact, look up official documentation for the exact version, confirm every API/class/function exists in that exact version, and re-run per dependency at point of use.
- **R-ENV-004** MUST: Execute environment file hydration calls at the earliest entrypoint phase before importing modules that depend on runtime configuration.
- **R-ENV-005** MUST: Wrap directory paths retrieved from environment variables in standard filesystem path objects rather than performing raw string operations.
- **R-ENV-006** MUST: Apply immediate type casting and format validation guards at module initialization to halt execution on invalid environment inputs.

### Verify

```bash
# Discover and execute the repository static analysis and configuration verification scripts to validate that all service endpoints and directory paths are read via environment variable accessors.
# Discover and execute the repository test suite with environment variables unset to confirm that default fallbacks allow local startup and that secret tokens fail fast.
# Discover the dependency manifest and authoritative lock artifact to verify all declared runtime environment and configuration libraries match the exact locked versions.
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification. Pull requests containing hardcoded operational endpoints or credentials fail automated quality gates, and violations must be refactored to use standard environment variable extraction before merging.
</enforcement>