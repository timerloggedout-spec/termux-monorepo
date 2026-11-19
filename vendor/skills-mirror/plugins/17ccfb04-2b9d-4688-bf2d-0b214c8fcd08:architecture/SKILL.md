---
description: Produce a lightweight architecture blueprint (services, events, file structure, open questions) before generating code.
status: beta
argument-hint: "<problem statement> [--async] [--kafka|--rabbitmq]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/architecture_design.py" $ARGUMENTS`

Show the markdown blueprint. The blueprint ends with a ready-to-run `one-shot-generator` command -- offer the user the choice between accepting that command or adjusting the constraints first.
