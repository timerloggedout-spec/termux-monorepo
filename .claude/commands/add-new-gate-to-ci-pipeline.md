---
name: add-new-gate-to-ci-pipeline
description: Workflow command scaffold for add-new-gate-to-ci-pipeline in termux-monorepo.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-gate-to-ci-pipeline

Use this workflow when working on **add-new-gate-to-ci-pipeline** in `termux-monorepo`.

## Goal

Implements a new CI gate (e.g., runtime smoke test) into the project pipeline, including code, CI workflow, and documentation.

## Common Files

- `scripts/ci/{gate_name}.py`
- `.github/workflows/{gate_name}.yml`
- `docs/{GATE_NAME}.md`
- `docs/ARCHW1Z-GATE.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Implement the gate logic as a script (e.g., Python, Bash).
- Add a new workflow YAML file to .github/workflows to run the gate in CI.
- Document the gate in a dedicated markdown file in docs/.
- Update architectural documentation to reflect the new gate's position in the pipeline.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.