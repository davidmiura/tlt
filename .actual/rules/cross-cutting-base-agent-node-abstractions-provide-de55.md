---
version: 2
name: cross-cutting-base-agent-node-abstractions-provide-de55
description: "Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Base Agent Node Abstractions Provide Standardized"
metadata:
  actual:
    adr_id: de559b80-7efa-4aa9-a618-eb1accca0ae6
    status: accepted
    candidate_group_id: aeb302e6-723a-4cec-9f6d-28fc15080304
    evidence:
      source: deep
  scope:
    root: monorepo
    paths:
      - tlt/agents/ambient_event_agent/nodes/**
---

# Adoption of langchain_core.messages for Agent Conversation and Prompt Representation: Base Agent Node Abstractions Provide Standardized

Scope: applies to `monorepo/tlt/agents/ambient_event_agent/nodes/**`.

These rules are ALWAYS ACTIVE for all files matching the configured scope.

### Rules

- **R-MSG-001** SHOULD: Base agent node abstractions SHOULD provide standardized wrapper methods for appending SystemMessage, AIMessage, and HumanMessage instances to workflow state.
- **R-MSG-002** MANDATORY: Prior to writing code using versioned libraries, the consumer MUST inspect the dependency manifest, identify the build tool, inspect the repository lock or resolution artifact for the exact resolved version, and verify public API compatibility against documentation for that exact version.
- **R-MSG-003** MANDATORY: Agent nodes manipulating conversational state MUST instantiate messages using langchain_core.messages classes rather than raw strings or untyped dictionaries.

### Verify

```bash
# Discover and execute the repository static analysis and type checking suite
# Discover and execute the repository unit and integration test suite
```

**Accept when:**
- All agent nodes manipulating conversational state instantiate messages using langchain_core.messages classes.
- Message sequence definitions in LLM invocations pass structured SystemMessage and HumanMessage instances rather than raw strings or untyped dictionaries.
- The dependency lock verification step confirms exact resolved versions prior to integration.

<enforcement>
Claude Code MUST NOT skip or defer verification. Verified by automated static analysis and peer code reviews. Violations will be blocked from merging.
</enforcement>