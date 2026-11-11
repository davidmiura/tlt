---
version: 2
name: cross-cutting-service-modules-adapters-not-hardcode-058e
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Service Modules Adapters Not Hardcode Deployment"
metadata:
  actual:
    adr_id: 058e9f68-c29d-4ee9-bdf3-30792512add8
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

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Service Modules Adapters Not Hardcode Deployment

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-CFG-001** MUST_NOT: Service modules and adapters MUST_NOT hardcode deployment-specific hostnames, port numbers, filesystem paths, or network endpoints directly into application logic.

### Verify

```bash
# Discover and execute repository static analysis and configuration verification scripts
# Discover and execute the repository test suite with environment variables unset
# Discover the dependency manifest and authoritative lock artifact
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>