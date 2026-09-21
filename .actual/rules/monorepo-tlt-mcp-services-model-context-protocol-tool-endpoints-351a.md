# FastMCP Framework Adoption for Model Context Protocol Services: Model Context Protocol Tool Endpoints Registered

These rules are ALWAYS ACTIVE for all service components exposing Model Context Protocol tools, resources, or server transports to external clients and agents.

### Rules

- **R-MCP-001** MUST: Model Context Protocol tool endpoints MUST be registered through modular tool registration interfaces that delegate business logic to separate service state managers.

### Verify

```bash
# Discover and execute project static analysis and linting verification scripts
# Discover and execute the integration test suite targeting Model Context Protocol tool and resource contracts
```

**Accept when:**
- All Model Context Protocol tool endpoints and resource URIs respond according to declared contracts under automated verification suite execution.
- The protocol server successfully initializes and serves requests across both standard input-output and network transport modes without schema mismatch errors.

<enforcement>
Claude Code MUST NOT skip or defer verification. All pull requests violating boundary separation or introducing unapproved transport layers will be blocked during automated verification.
</enforcement>