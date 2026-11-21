---
description: Generate a strangler-pattern migration scaffold (router + adapter + dual-run + parity tests + rollback + cutover plan) for a legacy module.
status: beta
argument-hint: "--legacy <legacy.py> --new <new.py> --flag <FEATURE_FLAG>"
allowed-tools: Bash(python *)
destructive: true
read-only: false
---

```!
python -c "
import sys, json
from skills.one_shot_generator.scripts.strangler_pattern import StranglerGenerator  # noqa
" 2>/dev/null; \
python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/strangler_pattern.py"
```

After the scaffold is generated, walk the user through:
1. Which file to copy first (`strangler/router.py` -- it controls traffic).
2. How to set the feature flag (`<FEATURE_FLAG>_PCT=5` for canary).
3. When to run the parity tests (continuously, before each phase bump).
4. How to abort (`bash strangler/rollback.sh`).
