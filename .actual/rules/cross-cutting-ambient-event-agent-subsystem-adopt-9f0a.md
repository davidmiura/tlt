---
version: 2
name: cross-cutting-ambient-event-agent-subsystem-adopt-9f0a
description: "Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Ambient Event Agent Subsystem Adopt Tlt"
metadata:
  actual:
    adr_id: 9f0acbb3-150a-4c60-a0c6-c55ee1553107
    status: accepted
    candidate_group_id: 92a00aeb-12f9-4606-b2e1-cb0eea1f0284
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/**
---

# Adoption of tlt.agents.ambient_event_agent.state.state for Agent State Management: Ambient Event Agent Subsystem Adopt Tlt

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-ST-001** MUST: The ambient event agent subsystem MUST adopt tlt.agents.ambient_event_agent.state.state as the canonical source for shared agent state representation across all execution nodes and routing controllers.
- **R-ST-002** MANDATORY: Execute lock-version grounding in order (manifest, build tool, lock artifact, official docs, API confirmation, version-sensitive re-run) before writing code that uses a versioned library.
- **R-ST-003** MANDATORY: Discover and use the repository's native project static analysis, type checking, and test suite tools.

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