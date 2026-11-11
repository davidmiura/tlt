---
version: 2
name: cross-cutting-every-agent-workflow-node-component-bad1
description: "Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Every Agent Workflow Node Component Ambient"
metadata:
  actual:
    adr_id: bad1ecef-32d1-45c1-b7dc-f9e4a245efb8
    status: accepted
    candidate_group_id: 8338cac3-2465-4de2-8a0d-e2367dec5e66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Every Agent Workflow Node Component Ambient

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all agent node implementations within the ambient event agent subsystem.

### Rules

- **R-NODE-001** MUST: Every agent workflow node component in the ambient event agent subsystem MUST inherit from the BaseNode abstraction provided by tlt.agents.ambient_event_agent.nodes.base and initialize its unique node identifier via the superclass initializer.

### Verify

```bash
# Discover the project test runner and execute the test suite targeting agent workflow nodes to verify BaseNode contract compliance and state propagation.
# Discover the project static analysis or type inspection tool and run type checks to confirm all execute signatures match AgentState input and output contracts.
```

**Accept when:**
- All agent workflow node test suites pass without unhandled exceptions or state contract violations.
- Static type verification confirms all workflow nodes implement the asynchronous execute contract with AgentState.

<enforcement>
Claude Code MUST NOT skip or defer verification. Violation handling: Pull requests introducing node components that do not inherit from BaseNode or that violate the execute contract will be blocked from merging until refactored.
</enforcement>