---
description: Interactive tour that walks the user through one-shot-prompting capabilities and recommends a starting template.
status: experimental
argument-hint: "[choice — pass empty for the main menu]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

Render the initial tour state. The user picks an option, you call back into this script with their choice.

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/interactive_tour.py" --json`

Show the prompt + numbered options to the user. When they reply, transition to the next state by re-running the script with the chosen key. Stop when a `recommendation` state arrives -- that state contains the template id + ready-to-paste prompt.
