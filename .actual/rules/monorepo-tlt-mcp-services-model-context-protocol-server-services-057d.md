# FastMCP Framework Adoption for Model Context Protocol Services: Model Context Protocol Server Services Instantiate

These rules are ALWAYS ACTIVE for all service components exposing Model Context Protocol tools, resources, or server transports to external clients and agents.

### Rules

- **R-MCP-001** MUST: All Model Context Protocol server services MUST instantiate and expose external protocol capabilities through the FastMCP server framework.

### Verify

```bash
# Discover and execute the project's static analysis and linting verification scripts to validate protocol endpoint signatures and boundary constraints.
# Discover and execute the integration test suite targeting Model Context Protocol tool and resource contracts across supported transport modes.
```

**Accept when:**
- All Model Context Protocol tool endpoints and resource URIs respond according to declared contracts under automated verification suite execution.
- The protocol server successfully initializes and serves requests across both standard input-output and network transport modes without schema mismatch errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated integration tests validating tool registration, resource resolution, and transport readiness, as well as static analysis checks, are mandatory.
</enforcement>