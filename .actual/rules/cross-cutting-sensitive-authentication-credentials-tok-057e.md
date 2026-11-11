---
version: 2
name: cross-cutting-sensitive-authentication-credentials-tok-057e
description: "Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Sensitive Authentication Credentials Tokens Private Secrets"
metadata:
  actual:
    adr_id: 057ef2f1-e8a7-4dce-ba7a-d66a34892f5b
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

# Environment Variable Configuration Sourcing via os.getenv and load_dotenv: Sensitive Authentication Credentials Tokens Private Secrets

Scope: applies to `monorepo/tlt/adapters/discord_adapter/**`, `monorepo/tlt/agents/ambient_event_agent/**`, `monorepo/tlt/mcp_services/**`, `monorepo/tlt/services/tlt_service/**`.

These rules are ALWAYS ACTIVE for all microservices, client adapters, gateway proxies, and background agent nodes within the distributed runtime.

### Rules

- **R-ENV-001** MUST: Sensitive authentication credentials, API tokens, and private secrets MUST be retrieved from environment variables without default fallback values, raising an error or emitting a warning when absent.

### Verify

```bash
# Discover and execute repository static analysis and configuration verification scripts
# Discover and execute the test suite with environment variables unset to confirm local startup defaults and fast-fail behavior for secrets
# Discover dependency manifest and lock artifact to verify matching versions
```

**Accept when:**
- Static analysis detects no hardcoded service network endpoints, storage paths, or sensitive credential tokens within application source code.
- Service and adapter initialization succeeds under default local environments through predictable fallback values for operational parameters.
- Service initialization halts or emits explicit degradation warnings when mandatory authentication credentials are absent from the runtime environment.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated static analysis and peer code review enforce compliance with environment variable naming conventions and fallback standards.
</enforcement>