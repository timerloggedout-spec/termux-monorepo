---
description: 4-phase systematic root cause investigation. No guessing. Hypothesize ranked causes → Instrument logging → Observe output → Fix confirmed root cause only. Generates temporary instrumentation, analyzes evidence, applies targeted fix.
status: beta
argument-hint: "[error or symptom description] [@path/to/project] [--error-log=<file>]"
allowed-tools: none
destructive: false
read-only: true
---

Invoke the systematic-debug skill:

/one-shot-prompting:sys-debug $ARGUMENTS
