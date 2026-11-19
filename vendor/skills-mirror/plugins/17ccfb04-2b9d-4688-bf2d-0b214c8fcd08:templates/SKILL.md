---
description: Browse, search, and show curated one-shot-prompting templates (25+ proven prompts for messaging, APIs, deployment, observability, refactoring).
status: beta
argument-hint: "[list|show|search|tags] [args]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/template_library.py" $ARGUMENTS`

Examples:
- `/one-shot-prompting:templates list` -- show every template
- `/one-shot-prompting:templates list --tag messaging` -- only messaging templates
- `/one-shot-prompting:templates show msg-kafka-validate` -- full prompt for one template
- `/one-shot-prompting:templates search rate-limiter` -- keyword search
- `/one-shot-prompting:templates tags` -- list all tags

Show the script output verbatim. After showing, if the user looks like they're picking a template, suggest they copy the `prompt` field directly into a new chat with `/one-shot-prompting:one-shot-generator`.
