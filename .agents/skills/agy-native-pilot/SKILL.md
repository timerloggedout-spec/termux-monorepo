---
name: agy-native-pilot
description: Use native AGY agents for bounded, source-only issue work in an explicit workspace, with a sequential implementation and independent verification handoff.
---

# AGY Native Pilot

Use this workflow for a specifically scoped issue that can be handled within its named source workspace.

1. State the issue, authorized workspace, allowed files, expected result, and local checks explicitly.
2. Assign implementation to `agy-implementer`. Keep the task source-only and bounded; do not include unrelated work.
3. After implementation finishes, assign `agy-verifier` to independently inspect the change and run relevant local checks. Run them sequentially: one writer followed by one verifier, to minimize quota use.
4. Review both reports and summarize changed paths, checks, and unresolved findings.

Do not treat these prose instructions as a permission sandbox. Preserve high verbosity and global auto-approve behavior. Never access Origin, global settings, or credentials, or publish/push/commit. Avoid recursion, background work, and network access unless explicitly requested and authorized.
