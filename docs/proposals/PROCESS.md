# Proposal Process — ArchW1z

Structured lifecycle so agents and humans share one pipeline: **ingest → register → itemize → review → execute → close**.

## Directory layout

```
docs/proposals/
  README.md                 # index + quick start
  PROCESS.md                # this file
  AGENTIC-PERMISSIONS.md    # what blocks full autonomy
  registry.yaml             # machine-readable status (agents read this first)
  _template/
    MANIFEST.md             # copy for new proposals
  active/
    <proposal-id>/
      MANIFEST.md           # metadata, reviewers, checklist
      ITEMS.md              # itemized work units
      source.md             # optional local copy / excerpt
      # OR source points at legacy flat file until migrated
  closed/
    <proposal-id>/          # same shape; status=closed
  legacy/                   # unmigrated flat dumps (read-only)
```

## States

| State | Meaning |
|-------|--------|
| `draft` | Author still writing |
| `posted` | Registered in `registry.yaml`; open for review |
| `in_review` | At least one reviewer assigned |
| `accepted` | Disposition agreed; execution may start |
| `executing` | Agents implementing itemized work |
| `blocked` | Waiting on permission / human-only step |
| `closed` | Done or explicitly rejected; moved to `closed/` |

## Roles

| Role | Who | Duties |
|------|-----|--------|
| **Author** | Human or agent that posted the proposal | Owns intent |
| **Registrar** | Agent (preferred) | Creates folder, registry row, ITEMS skeleton |
| **Reviewer** | Named agent or human | Signs REVIEW section; may REQUEST_CHANGES |
| **Executor** | Agent with write access | Implements accepted items through gates |
| **Closer** | Reviewer or author | Moves to `closed/`, updates registry |

## Required MANIFEST fields

```yaml
id: chatgpt-critical-eval
title: "Critical Eval TER0-15 + branches"
author: ChatGPT
posted_at: 2026-08-02
source: legacy/ChatGPT_Critical-Eval.md   # or active/.../source.md
status: executing
priority: P0
reviewers:
  - id: grok-archw1z
    role: reviewer+executor
    status: accepted
    at: 2026-08-02
  - id: chatgpt
    role: author
    status: posted
    at: 2026-08-02
related_prs: [2, 3, 5, 6, 9, 10, 11]
related_branches: [master-staging, termux-smoke]
gates_required: [repo-gate, termux-smoke]
```

## Itemization rules (ITEMS.md)

Every actionable claim becomes a row:

| ID | Claim / work | Priority | Owner | Status | Evidence |
|----|--------------|----------|-------|--------|----------|
| CE-01 | Install repo-gate on master-staging | P0 | grok | done | commits … |

Statuses: `todo` | `doing` | `done` | `blocked` | `wontfix`

Agents **must not** invent work outside ITEMS without adding a row first.

## Review posting protocol

1. Registrar creates `active/<id>/` + registry entry (`status: posted`).
2. Reviewers append to MANIFEST `reviewers[]` and write notes under `## Review log`.
3. On consensus → `status: accepted` → Executor may open PRs targeting `master-staging`.
4. Each merge references item IDs in the commit/PR body (`Implements: CE-01`).
5. When all items terminal → Closer sets `closed` and moves tree to `closed/`.

## Gate coupling

No proposal execution merges to `master` without:

1. `repo-gate` green
2. `termux-smoke` green
3. Item IDs cited
4. No unresolved **critical** review threads on the PR

## Agent entrypoint

```text
1. Read docs/proposals/registry.yaml
2. Pick highest-priority accepted/executing item that is todo
3. Implement on branch off master-staging
4. PR → master-staging with Implements: <ITEM-ID>
5. Update ITEMS.md + registry.yaml in same PR when possible
```
