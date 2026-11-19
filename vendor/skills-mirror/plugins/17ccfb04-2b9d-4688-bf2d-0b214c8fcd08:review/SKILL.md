---
description: Run the automated code-review gates (lint / security / performance / type / test coverage) over a file.
argument-hint: "<path/to/file>"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/code_review_automation.py" "$ARGUMENTS"`

Render the JSON report inline. If `overall == BLOCK`, stop the user from merging until the listed issues (security or hardcoded secrets) are addressed. If `WARN`, surface the findings but allow them to proceed.
