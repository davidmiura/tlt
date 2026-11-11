---
version: 2
name: cross-cutting-every-agent-execution-node-implementatio-1bc8
description: "Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Every Agent Execution Node Implementation Accept"
metadata:
  actual:
    adr_id: 1bc8d762-4bd5-4cc8-b11a-02cd7447b53a
    status: accepted
    candidate_group_id: 92a00aeb-12f9-4606-b2e1-cb0eea1f0284
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/**
---

# Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Every Agent Execution Node Implementation Accept

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/**`.

These rules are ALWAYS ACTIVE for all asynchronous node implementations within the ambient event agent subsystem and routing and decision controllers managing execution transitions for agent workflows.

### Rules

- **R-STATE-001** MUST: Every agent execution node implementation MUST accept AgentState as its primary execution parameter and return the updated AgentState upon completion.
- **R-STATE-002** MANDATORY: The consumer MUST derive tool names, file names, commands, package managers, and version numbers from the project repository.
- **R-STATE-003** MANDATORY: Before writing code that uses a versioned library, execute the lock-version grounding sequence (manifest inspection, build tool identification, lock file artifact verification, official documentation lookup, API existence confirmation, and dependency re-verification at point of use).
- **R-STATE-004** MANDATORY: When introducing new workflow nodes, implement the asynchronous execution contract accepting and returning the canonical state structure.
- **R-STATE-005** MANDATORY: Group specialized operational state into structured sub-dictionaries or sub-models within the state contract to prevent top-level namespace collisions.

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
Claude Code MUST NOT skip or defer verification. Automated static type analysis and continuous integration test suites validate agent state mutation during end-to-end execution cycles. Peer code review is required for any pull request modifying the shared state schema or node execution contracts. Pull requests introducing out-of-band state mutation or alternative state schemas are blocked at continuous integration.
</enforcement>