---
description: Run a kaizen retrospective on an agentic-harness run and file tool-improvement feedback upstream (invokes the harness-feedback skill).
argument-hint: "[optional: a quick note on what to give feedback about]"
---

Run a kaizen / postmortem retrospective on the most recent agentic-harness work and, with my
explicit approval, file tool-improvement feedback as a GitHub issue on the upstream
`MrBogomips/agentic-harness` repository.

Invoke the **harness-feedback** skill and follow it end to end: establish the run context, walk the
retrospective, draft in the standard feedback format, redact project-identifying details, pass the
completeness gate, and create the issue only after I approve the exact body. If `gh` is unavailable
or unauthenticated, give me a prefilled new-issue URL instead.

Starting note (optional): $ARGUMENTS
