---
version: 2
name: cross-cutting-execution-nodes-encapsulate-transient-ra-9324
description: "Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Execution Nodes Encapsulate Transient Rate Limiting"
metadata:
  actual:
    adr_id: 93241144-ef9a-4058-a394-d2f9a4dd36b9
    status: accepted
    candidate_group_id: 92a00aeb-12f9-4606-b2e1-cb0eea1f0284
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/**
---

# Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Execution Nodes Encapsulate Transient Rate Limiting

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-AST-001** SHOULD: Execution nodes SHOULD encapsulate transient rate-limiting timestamps and local operational tracking within the node instance while persisting workflow-critical outcomes to the shared state object.

### Verify

```bash
# Discover and execute project static analysis and type checking across agent modules
# Discover and run the automated test suite covering agent node execution and routing transitions
```

**Accept when:**
- All agent execution node contracts accept and return the canonical AgentState type without type checking errors.
- All route transition functions derive routing decisions exclusively from fields declared in the shared state contract.
- Repository test suites for agent workflow execution and state transitions pass without regressions.

<enforcement>
Claude Code MUST NOT skip or defer verification.
</enforcement>