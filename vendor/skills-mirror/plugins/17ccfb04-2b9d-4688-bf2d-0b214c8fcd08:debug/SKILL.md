---
description: Pattern-match an error / stack trace and return ranked fixes plus a repro snippet (event-driven failure modes).
argument-hint: "<paste error or stack trace>"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

Pipe the user's error text to the debugging helper:

!`echo "$ARGUMENTS" | python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/debugging_helpers.py"`

The script returns a JSON diagnosis with:
- `pattern` (handler-timeout, queue-backpressure, schema-mismatch, ...)
- `root_cause` -- one-line hypothesis
- `fixes` -- ranked by likelihood
- `repro` -- minimal pytest snippet to confirm the diagnosis locally

Show the JSON, then summarise: which fix to try first, and how to run the repro.
