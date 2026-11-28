---
description: End-to-end agentic one-shot. Understands multi-entity intent, scans the existing codebase, spawns architect → implementer → test-author → reviewer → wirer → critic agents, verifies + auto-patches, and ships working code. Use --templated for the legacy script-only fallback.
argument-hint: "[feature description] [@path/to/project] [--apply] [--templated] [--budget=USD] [--review] [--force]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
destructive: true
read-only: false
---

Invoke the **one-shot-generate** skill:

/one-shot-prompting:one-shot-generate $ARGUMENTS

This is the *agentic* path:
1. scans the user's codebase (deterministic)
2. extracts the domain model from natural language
3. consults the failure curriculum to avoid past mistakes
4. **spawns the architect agent** via Task — produces spec.json
5. **spawns implementer + test-author agents in parallel** via Task — write code from spec
6. runs verifier + auto-patch (deterministic services)
7. **spawns the reviewer agent** via Task — security/perf/style gate
8. wires generated code into main.py / urls.py
9. **spawns the critic agent** via Task — runs pytest, decides ship-vs-loop

For pure deterministic generation (no Claude tokens; lower quality, free),
pass `--templated`. The skill will route to the legacy
`one_shot_orchestrator.py` Python pipeline instead.
