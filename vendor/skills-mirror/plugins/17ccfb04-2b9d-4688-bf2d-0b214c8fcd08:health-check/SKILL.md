---
description: Scan the current project and report what one-shot-prompting can generate for it (framework, bus, testing, IaC, migrations).
argument-hint: "[@path/to/project]"
allowed-tools: Bash(python *)
destructive: false
read-only: true
---

Run a capability scan over the project at $ARGUMENTS (or the current directory if no path is given) and produce a compact health report.

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/health_check.py" "$ARGUMENTS"`

The report shows:
- detected framework, message bus, runtime, testing tool, logger, IaC, migrations
- which plugin capabilities are unlocked given that stack
- recommendations for closing gaps before generation

Show the user the report verbatim. If the scan flagged missing pieces, suggest the closest matching template from the template library (e.g. `obs-otel-prom` if observability is missing, `deploy-k8s-bundle` if Dockerfile is missing).
