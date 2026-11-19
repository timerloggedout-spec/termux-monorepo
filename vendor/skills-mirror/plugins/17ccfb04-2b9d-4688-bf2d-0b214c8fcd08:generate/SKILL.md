---
description: Generate a complete sidecar feature module in one response. No approval gate. Claude makes decisions, states assumptions, ships the code. Rerun with constraints if you disagree.
status: experimental
argument-hint: "[feature description]"
allowed-tools: Read, Write, Glob, Grep
destructive: false
read-only: true
---

Generate a complete sidecar feature module for this request.

**Feature:** $ARGUMENTS

Use the one-shot-generator skill. Produce in ONE response:

1. Assumptions block stating every non-trivial decision and why
2. Complete module file
3. Test file with at least two tests
4. README with events, command, adaptation notes
5. One-line install instruction
6. Rerun hints for how to override key assumptions

Do NOT ask me clarifying questions. Pick defensible defaults, state them in the assumptions block, ship the code. If I disagree, I'll rerun with specific overrides.

If the request is multi-feature, cross-cutting, or not sidecar-shaped, refuse with a specific reason and stop. Don't start a conversation.

Assume:
- My project has (or will use) an async event bus
- I want idiomatic code in whatever language my project uses (infer from context or default to Python)
- I'll adapt bus method names to my actual system using your adaptation notes
