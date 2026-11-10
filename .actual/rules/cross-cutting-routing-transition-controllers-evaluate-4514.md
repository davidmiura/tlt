---
version: 2
name: cross-cutting-routing-transition-controllers-evaluate-4514
description: "Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Routing Transition Controllers Evaluate Execution Status"
metadata:
  actual:
    adr_id: 4514c950-d904-4b57-83a0-4992ec109520
    status: accepted
    candidate_group_id: 92a00aeb-12f9-4606-b2e1-cb0eea1f0284
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/**
---

# Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Routing Transition Controllers Evaluate Execution Status

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-STATE-001** MUST: Routing and transition controllers MUST evaluate execution status, processing steps, and iteration limits exclusively through the fields defined in tlt.agents.ambient_event_agent.state.state.

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