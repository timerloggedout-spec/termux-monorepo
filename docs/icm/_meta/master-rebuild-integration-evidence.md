# Master Rebuild Integration Evidence

## Purpose

This record preserves the review and learning value of PR #232's pre-rebuild ancestry without carrying unrelated application, CI, workflow, and governance changes into the documentation-only ICM integration branch. The active ICM branch is rebuilt from the current `master`; this record is the permanent map back to the preserved material.

> **Boundary:** This is an evidence index, not approval to merge, cherry-pick, execute, or deploy any archived change. Each candidate requires its own owner, scope, validation, and review before separate integration.

## Immutable preservation point

| Item | Value | Role |
|---|---|---|
| Archive branch | `archive/pr232-pre-master-rebuild-20260817` | Read-only review source; no pull request is opened from it automatically. |
| Archived tip | `52dcc83ffb0010305bacfae24862c3440d5aa939` | Exact pre-rebuild tip of PR #232 before its master reset. |
| Current master at assessment | `efd57173fcad33f2d4ca4faec303918bbecdf961` | Target baseline used to remove master conflicts. |
| Master-staging ancestor | `c3ac8f632746967b16785bd1e459d6f5960bba53` | Parent lineage that brought the inherited change set into the original PR branch. |
| Divergence base | `320c73beb9eaf834acb3efebcec8aeddbd44e6d7` | Common ancestor of current `master` and the archived tip. |

## Review workflow

When an archived change becomes relevant, compare the archived path against the version on current `master`, identify its original issue/PR and owner, make a fresh scoped proposal, and then open or update a dedicated review path. Do not recover an archived file wholesale merely to eliminate a conflict.

| Area | Conflicted paths | Preservation intent | Integration condition |
|---|---|---|---|
| Repository policy and root entry points | `.coderabbit.yaml`, `AGENTS.md`, `README.md` | Preserve prior policy and agent-entrypoint experiments for comparison. | Explicit governance review against current repository policy. |
| GitHub automation and provider execution | `.github/connectors/github.yaml`, `.github/workflows/agent-feedback-linear-sync.yml`, `.github/workflows/agent-jules-on-issues.yml`, `.github/workflows/agent-review-auto-jules.yml`, `.github/workflows/gemini-dispatch.yml`, `.github/workflows/gemini-invoke.yml`, `.github/workflows/gemini-review.yml`, `.github/workflows/gemini-triage.yml`, `.github/workflows/repo-gate.yml` | Preserve workflow strategies, provider scope, quota controls, and trigger experiments. | Dedicated workflow/provider review with secrets, permissions, cost, and CI validation. |
| Jules operating materials | `.jules/bolt.md`, `.jules/sentinel.md` | Preserve operational-agent concepts and historical prompts. | Owner-approved Jules/session-management scope. |
| Application and CI code | `archwiz/archwiz.py`, `deepcli/deepcli/core.py`, `scripts/ci/repo_gate.py`, `termux-multi-agent/dashboard.py` | Preserve implementation alternatives as ML-pipeline training/context evidence. | Separate code change with focused tests and code review. |
| Governance and proposal materials | `docs/CONSENSUS.md`, `docs/proposals/AGENTIC-PERMISSIONS.md`, `docs/proposals/PROCESS.md`, `docs/proposals/README.md`, `docs/proposals/corrected_cloud_offload_evaluation.md`, `docs/proposals/registry.yaml` | Preserve competing governance patterns, proposal definitions, and registration data. | Governance reconciliation with explicit record ownership and registry conflict resolution. |

## ICM replay scope

The following commits are the bounded ICM integration sequence replayed onto current `master`. They are intentionally distinct from the archived inherited material.

| Original commit | Subject |
|---|---|
| `486a4f9136dacad3607e8cdede45db5a9c9ac984` | `feat(submodule): add ICM Architect fork` |
| `06e938054eb612b3dfdd598a209e2b2f047a9570` | `docs(icm): map monorepo intended usage` |
| `d02abeb7061deb5c6eaad6c14c5dac107c22151b` | `docs(icm): add maintenance pipeline` |
| `e0bb029c6cdaa02e7a215810a76ecd1ebe8692b6` | `docs(icm): add methodology companion` |
| `f63bb1a88ffa9f2f09c3b5c4902803e0b0a65c4d` | `docs(icm): reconcile related pull requests` |
| `52dcc83ffb0010305bacfae24862c3440d5aa939` | `docs(icm): add native reference input routes` |

## Evidence sources

1. Git’s non-mutating three-way merge simulation at the assessment refs above yielded 24 conflicts: 9 GitHub automation/configuration files, 4 application or CI files, 2 Jules files, 3 root files, and 6 governance/documentation files.
2. The archive branch preserves the exact original PR tip, including all six ICM commits and inherited master-staging changes, for future review.
3. The rebuilt PR branch intentionally contains only the replayed ICM documentation/submodule scope and follow-on ICM artifacts.
