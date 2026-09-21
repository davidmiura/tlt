# dotenv for Runtime Environment Configuration Management: Configuration Extractions Non Secret Operational Parameters

These rules are ALWAYS ACTIVE for all standalone microservices, protocol gateways, and external integration adapters requiring runtime configuration.

### Rules

- **R-CFG-001** MUST: Configuration extractions for non-secret operational parameters MUST provide safe default fallback values in os.getenv calls to support local execution.

### Verify

```bash
# Discover the project test runner from repository configuration manifests and execute the test suite covering service initialization and configuration loading.
# Discover and run repository static analysis tools to verify that credential extractions do not define hardcoded fallback strings.
```

**Accept when:**
- Configuration bootstrapping successfully resolves runtime parameters via the configuration library during service startup across all test environments.
- Service initialization routines fail fast with informative diagnostics when required security credentials are omitted from the environment.
- All non-secret configuration options default to safe local values when environment variables are unset.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>