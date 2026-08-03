# Linear Agent Protocol

**Status:** binding for all coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

Linear is the **operational tracker** for work that ships. Proposal process (`docs/proposals/PROCESS.md`) remains the debate/consensus layer; Linear tracks execution state, ownership, and git branch linkage.

Team: **Termux-monorepo_linear** (key prefix `TER-`)
Project: **termux-monorepo hardening**

---

## 1. Hard rules (agents MUST)

1. **Every non-trivial agent action** that creates a branch, opens a PR, or closes work **must** reference a Linear issue (`TER-N`).
2. Prefer **updating an existing TER-*** over creating a new one. Create only when no issue covers the work.
3. PR title or body **must** include `Implements: TER-N` (and proposal item IDs when applicable).
4. Branch names **should** match Linear’s suggested `gitBranchName` when starting from an issue (e.g. `timerloggedout/ter-14-…`).
5. On start of work → set Linear state to **In Progress**.
6. On PR open → comment on Linear issue with PR URL (or attach link).
7. On merge to `master-staging` (or close of work) → set Linear state to **Done** (or leave In Progress if residual).
8. Do **not** invent work outside Linear + `docs/proposals/active/*/ITEMS.md`. If needed, create Linear issue **and** ITEMS row.

Unposted chat is not Linear state. If it is not on the issue, it did not happen for tracking purposes.

---

## 2. State machine

| Linear state | When agents set it |
|--------------|--------------------|
| **Backlog** | Parked / not started |
| **Todo** | Ready to pick |
| **In Progress** | Agent started branch / PR |
| **Done** | Merged to `master-staging` or explicitly completed |
| **Canceled** | Won’t do (with reason in description) |
| **Duplicate** | Point to canonical TER-N |

Priority map: P0 → Urgent (1), P1 → High (2), P2 → Medium (3), P3 → Low (4).

---

## 3. Action → Linear hooks

| Agent action | Linear hook |
|--------------|-------------|
| Pick work | `list_issues` filter Todo/Backlog; claim via assignee if available |
| Start implementation | `save_issue` → state **In Progress**; ensure `gitBranchName` used |
| Open PR | Comment on issue with PR URL; body `Implements: TER-N` |
| Push significant commits | Optional short comment (milestone only; avoid noise) |
| PR merged to `master-staging` | state **Done**; append evidence (PR/commit) to description |
| Blocked (human-only) | Comment + leave **In Progress** or move **Backlog**; cite `AGENTIC-PERMISSIONS.md` |
| New work discovered | `save_issue` create; link parent if sub-task; add ITEMS row |
| Close proposal | Ensure related TER-* are Done/Canceled; comment cross-ref |

### MCP tools (Grok / connected agents)

```
linear___list_issues          # discover / filter
linear___get_issue            # full detail
linear___save_issue           # create or update (id=TER-N)
linear___list_comments        # thread
linear___list_issue_statuses  # state names for team
linear___save_document        # optional long-form on issue/project
```

### On-device / CI (no MCP)

```bash
export LINEAR_API_KEY="lin_api_..."
python3 archwiz/linear_sync.py --dry-run   # report
python3 archwiz/linear_sync.py             # push local taDone → Linear states
python3 -m archwiz.linear_client status TER-14
python3 -m archwiz.linear_client start TER-14
python3 -m archwiz.linear_client done TER-14 --pr 16
```

See `archwiz/linear_client.py`.

---

## 4. Create vs update template

**Create (only if no existing TER-* fits):**

```text
Title: <imperative, scoped>
Team: Termux-monorepo_linear
Project: termux-monorepo hardening
Priority: 1–4
Description:
  ## Goal
  ...
  ## Context
  ...
  ## Acceptance
  - [ ] ...
  Implements proposal item: <ITEM-ID> (if any)
```

**Update on start:**

```text
id: TER-N
state: In Progress
# optional: assignee me, links [{url, title}]
```

**Update on complete:**

```text
id: TER-N
state: Done
# description append: Evidence: PR #X merged YYYY-MM-DD
```

---

## 5. Relationship to proposal process

```text
registry.yaml / ITEMS.md     ← consensus & itemization (PROCESS.md)
        ↕ must cite each other
Linear TER-*                 ← execution board (this protocol)
        ↕ Implements: TER-N
GitHub PR → master-staging   ← code
```

- Proposal **ITEMS** may map 1:1 or N:1 to TER-*.
- PR must cite **both** when both exist: `Implements: TER-14, M-02`.
- Closing a proposal does not auto-close Linear; agents close TER-* explicitly.

---

## 6. TER-14 scope

**TER-14** = Sentry multi-project + Linear GraphQL bridge + **this protocol**.

Related:
- TER-5 (dispatch logging) — observability adjacent
- TER-2 (tools connected) — Done; MCP available
- Manus PR #13 — path norm + mock bridge (superseded for Linear by PR #16)

When Sentry+Linear PR merges to `master-staging`, mark **TER-14 Done**.

---

## 7. Checklist (paste into agent runbooks)

```text
[ ] Read AGENTS.md + this protocol
[ ] list_issues — pick or create TER-N
[ ] save_issue → In Progress
[ ] Branch from master-staging (prefer Linear gitBranchName)
[ ] Implement; commits reference TER-N
[ ] PR → master-staging with Implements: TER-N
[ ] Comment on Linear issue with PR URL
[ ] Gates green; merge
[ ] save_issue → Done + evidence
[ ] Update ITEMS.md if proposal-linked
```

---

## 8. Failure modes

| Symptom | Action |
|---------|--------|
| No LINEAR_API_KEY on device | Use MCP tools only; or dry-run `linear_sync.py` |
| MCP write denied | Fall back to GitHub issue comment + request Operator grant |
| Orphan PR (no TER-*) | Open/link TER-* before merge; do not merge orphan P0 |
| Duplicate TER-* | Mark Duplicate; point to canonical |
