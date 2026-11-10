---
version: 2
name: cross-cutting-every-basenode-subclass-implement-asynch-5d6b
description: "Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Every Basenode Subclass Implement Asynchronous Execute"
metadata:
  actual:
    adr_id: 5d6bf83d-75ce-4635-9add-971b9a469a85
    status: accepted
    candidate_group_id: 8338cac3-2465-4de2-8a0d-e2367dec5e66
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of BaseNode Execution Abstraction in tlt.agents.ambient_event_agent.nodes.base: Every Basenode Subclass Implement Asynchronous Execute

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all agent node implementations within the ambient event agent subsystem.

### Rules

- **R-BASE-001** MUST: Every BaseNode subclass MUST implement the asynchronous execute contract accepting an AgentState instance and returning the updated AgentState instance.

### Verify

```bash
# Discover and run the project test runner targeting agent workflow nodes
pytest tests/agents/ambient_event_agent/nodes/

# Discover and run static analysis/type checking
mypy tlt/agents/ambient_event_agent/nodes/
```

**Accept when:**
- All agent workflow node test suites pass without unhandled exceptions or state contract violations.
- Static type verification confirms all workflow nodes implement the asynchronous execute contract with AgentState.

<enforcement>
Claude Code MUST NOT skip or defer verification. All agent pipeline node contributions must be verified via static type analysis and automated integration tests.
</enforcement>