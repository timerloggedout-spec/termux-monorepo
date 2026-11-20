---
description: Scan the project for cross-module inconsistencies (mixed serializers / loggers / error handling) and propose a shared library.
argument-hint: "[@path/to/project]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/consistency_checker.py" "$ARGUMENTS"`

Show the JSON report. If `inconsistencies` is non-empty, suggest running:
`/one-shot-prompting:standardize` (which calls `consistency_checker.py` again and writes the proposed shared library skeleton).
