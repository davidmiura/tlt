---
version: 2
name: cross-cutting-agent-nodes-not-represent-prompts-162c
description: "Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Agent Nodes Not Represent Prompts Conversation"
metadata:
  actual:
    adr_id: 162c30de-5304-46c8-ae4f-1fade1d69cf0
    status: accepted
    candidate_group_id: aeb302e6-723a-4cec-9f6d-28fc15080304
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Agent Nodes Not Represent Prompts Conversation

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all ambient agent graph node implementations and state transitions.

### Rules

- **R-ACT-001** MUST_NOT: Agent nodes MUST NOT represent prompts or conversation history as unvalidated primitive string lists or untyped dictionary collections.

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