---
version: 2
name: cross-cutting-consumers-discover-repository-dependency-7441
description: "Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Consumers Discover Repository Dependency Lock Artifact"
metadata:
  actual:
    adr_id: 7441f85f-31e5-410d-816a-d7bb9a962233
    status: accepted
    candidate_group_id: aeb302e6-723a-4cec-9f6d-28fc15080304
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Consumers Discover Repository Dependency Lock Artifact

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all ambient agent graph node implementations and state transitions.

### Rules

- **R-ADR-001** MUST: Consumers MUST discover the repository dependency lock artifact and resolve the exact locked version before invoking framework messaging APIs.

### Verify

```bash
# Discover and execute the repository static analysis and type checking suite to verify message class imports and usage across agent nodes.
# Discover and execute the repository unit and integration test suite to validate prompt creation and state message tracking.
```

**Accept when:**
- All agent nodes manipulating conversational state instantiate messages using langchain_core.messages classes.
- Message sequence definitions in LLM invocations pass structured SystemMessage and HumanMessage instances rather than raw strings or untyped dictionaries.
- The dependency lock verification step confirms exact resolved versions prior to integration.

<enforcement>
Claude Code MUST NOT skip or defer verification. All agent pipeline changes are verified by automated static analysis and peer code reviews.
</enforcement>