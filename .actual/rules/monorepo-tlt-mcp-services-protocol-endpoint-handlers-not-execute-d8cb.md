# FastMCP Framework Adoption for Model Context Protocol Services: Protocol Endpoint Handlers Not Execute Direct

These rules are ALWAYS ACTIVE for all service components exposing Model Context Protocol tools, resources, or server transports to external clients and agents.

### Rules

- **R-MCP-001** MUST_NOT: Protocol endpoint handlers MUST NOT execute direct disk state mutations or business logic inline without delegating to dedicated service layer abstractions.

### Verify

```bash
# Discover and execute the project's static analysis and linting verification scripts
# Discover and execute the integration test suite targeting Model Context Protocol tool and resource contracts
```

**Accept when:**
- All Model Context Protocol tool endpoints and resource URIs respond according to declared contracts under automated verification suite execution.
- The protocol server successfully initializes and serves requests across both standard input-output and network transport modes without schema mismatch errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. Automated integration tests, static analysis checks, and peer code reviews enforce protocol layer boundary separation.
</enforcement>