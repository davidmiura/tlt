---
version: 2
name: cross-cutting-node-implementations-encapsulate-executi-f9a0
description: "Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Node Implementations Encapsulate Execution Logic Within"
metadata:
  actual:
    adr_id: f9a051c1-a62b-4664-922e-6fd4b4d3b4c2
    status: accepted
    candidate_group_id: 8338cac3-2465-4de2-8a0d-e2367dec5e66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Node Implementations Encapsulate Execution Logic Within

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all agent node implementations within the ambient event agent subsystem.

### Rules

- **R-NODE-001** MUST: Node implementations MUST encapsulate execution logic within structured error handling blocks and invoke handle_error on caught exceptions to maintain deterministic agent state status transitions.

### Verify

\`\`\`bash
# Discover the project test runner and execute the test suite targeting agent workflow nodes
# Discover the project static analysis or type inspection tool and run type checks
pytest tests/agents/ambient_event_agent/nodes/
mypy tlt/agents/ambient_event_agent/nodes/
\`\`\`

**Accept when:**
- All agent workflow node test suites pass without unhandled exceptions or state contract violations.
- Static type verification confirms all workflow nodes implement the asynchronous execute contract with AgentState.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verification is mandatory via static type analysis and automated integration tests.
</enforcement>