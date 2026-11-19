---
description: Enforce Red-Green-Refactor TDD cycle with phase gates. Generates failing test first (RED), then minimal implementation (GREEN), then aligned refactoring (REFACTOR). Each phase blocked until previous phase verified.
status: beta
argument-hint: "[feature description] [@path/to/project] [--phase=red|green|refactor]"
allowed-tools: none
destructive: true
read-only: false
---

Invoke the tdd-cycle skill:

/one-shot-prompting:tdd-cycle $ARGUMENTS
