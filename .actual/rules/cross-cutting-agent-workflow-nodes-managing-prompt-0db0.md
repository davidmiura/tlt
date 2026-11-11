---
version: 2
name: cross-cutting-agent-workflow-nodes-managing-prompt-0db0
description: "Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Agent Workflow Nodes Managing Prompt Construction"
metadata:
  actual:
    adr_id: 0db036b9-8145-48eb-83aa-ca230cc8a58a
    status: accepted
    candidate_group_id: aeb302e6-723a-4cec-9f6d-28fc15080304
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Agent Workflow Nodes Managing Prompt Construction

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all agent workflow nodes managing prompt construction and conversational history.

### Rules

- **R-MSG-001** MUST: All agent workflow nodes managing prompt construction and conversational history MUST use langchain_core.messages classes including SystemMessage, AIMessage, and HumanMessage.

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
Claude Code MUST NOT skip or defer verification.
</enforcement>