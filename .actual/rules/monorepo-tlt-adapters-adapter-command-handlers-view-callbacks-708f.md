# Discord Interaction Handling via Ephemeral Response Messaging: Adapter Command Handlers View Callbacks Processing

These rules are ALWAYS ACTIVE for all Discord chat platform integration adapters, command handlers, user interface views, and modals processing incoming guild and user interaction events.

### Rules

- **R-DISCORD-001** MUST: All adapter command handlers and view callbacks processing incoming discord interaction requests MUST respond through interaction response methods with ephemeral delivery enabled for validation, error notifications, and user-scoped command feedback.
- **R-DISCORD-002** EXCEPTION (EXC-27-001): A command explicitly publishes a public guild announcement intended for all channel members rather than an individual invoking user.
- **R-DISCORD-003** MANDATORY: Implement permission validation guards at the entry point of each interaction handler before invoking backend integration clients.
- **R-DISCORD-004** MANDATORY: Encapsulate interactive user confirmation workflows within dedicated modal components rather than multi-message channel exchanges.
- **R-DISCORD-005** DISCOVERY POLICY (MANDATORY): This ADR omits all tool names, file names, commands, package managers, and version numbers. The consumer MUST derive them from the project repository.
- **R-DISCORD-006** LOCK-VERSION GROUNDING (MANDATORY) — before writing code that uses a versioned library, execute in order:
  1. Find the dependency manifest in the repo. It declares ranges, not installed versions.
  2. Identify the build tool from the manifest.
  3. Inspect the repository lock or resolution artifact to determine the exact resolved version. This artifact is authoritative; build-tool output only verifies the active environment matches it.
  4. Look up the official documentation, changelog, or public API reference for that exact version. Do not use training-data recall — fetch or search the public internet for version-specific docs.
  5. Confirm every API, class, or function you will call exists in that exact version's documentation before using it.
  6. For version-sensitive behavior, re-run steps 3-5 per dependency at point of use.

### Verify

```bash
# Discover and execute the project test suite runner to validate adapter interaction handler compliance.
# Discover and execute the project static analysis and linting verification scripts to check interaction response configurations.
```

**Accept when:**
- All adapter command handlers and UI interaction callbacks pass automated unit and integration tests.
- Static analysis confirms all validation notices, permission rejections, and intermediate interaction states route through ephemeral response mechanisms.

<enforcement>
Claude Code MUST NOT skip or defer verification. Continuous integration test suites validate interaction handler response flags and exception handling.
</enforcement>