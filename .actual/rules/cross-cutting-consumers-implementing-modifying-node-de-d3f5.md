---
version: 2
name: cross-cutting-consumers-implementing-modifying-node-de-d3f5
description: "Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Consumers Implementing Modifying Node Dependencies Discover"
metadata:
  actual:
    adr_id: d3f59a84-3dd2-4995-a660-8268f93e024d
    status: accepted
    candidate_group_id: 8338cac3-2465-4de2-8a0d-e2367dec5e66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Consumers Implementing Modifying Node Dependencies Discover

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all agent node implementations within the ambient event agent subsystem.

### Rules

- **R-NODE-001** MUST: Consumers implementing or modifying node dependencies MUST discover the ecosystem lock artifact and verify the exact resolved dependency versions prior to introducing external libraries.

### Verify

```bash
# Discover the project test runner and execute the test suite targeting agent workflow nodes
# to verify BaseNode contract compliance and state propagation.
# Discover the project static analysis or type inspection tool and run type checks
# to confirm all execute signatures match AgentState input and output contracts.
```

**Accept when:**
- All agent workflow node test suites pass without unhandled exceptions or state contract violations.
- Static type verification confirms all workflow nodes implement the asynchronous execute contract with AgentState.

<enforcement>
Claude Code MUST NOT skip or defer verification. All agent pipeline node contributions are verified by static type analysis, automated integration tests, and peer code review.
</enforcement>