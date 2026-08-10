# Proposal Process — ArchW1z

Structured lifecycle: **ingest → register → itemize → review → execute → close**.

**Also read:** `AGENTIC-PERMISSIONS.md` · `registry.yaml` · root `AGENTS.md` / `CONTRIBUTING.md`

---

## Directory layout

```
docs/proposals/
  README.md
  PROCESS.md                 # this file
  AGENTIC-PERMISSIONS.md
  registry.yaml              # agents read first
  _template/MANIFEST.md
  active/<id>/{MANIFEST.md,ITEMS.md,DEBATE.md?,source.md?}
  closed/<id>/
  legacy/                    # flat dumps, read-only
```

---
## States

| State | Meaning |
|-------|--------|
| `draft` | Author still writing |
| `posted` | In `registry.yaml`; open for review |
| `in_review` | ≥1 reviewer assigned |
| `accepted` | Disposition agreed; execution may start |
| `executing` | Items being implemented |
| `blocked` | Waiting on human-only or external step |
| `closed` | Terminal; tree under `closed/` |

---

## Roles

| Role | Who | Powers |
|------|-----|--------|
| **Author** | Poster of proposal | Owns intent; may close as `rejected` with reason |
| **Registrar** | Agent preferred | Creates folder + registry + ITEMS skeleton |
| **Reviewer** | Named agent or human | `accepted` / `changes_requested` / `commented` in MANIFEST |
| **Executor** | Write-capable agent | Implements *accepted* items via gates; cannot close P0 security alone |
| **Closer** | Reviewer **or** author (see closing rules) | Moves to `closed/`, updates registry |
| **Operator (human)** | Repo owner | Credential rotation, history rewrite auth, App permissions |

---

## Where proposals are debated

Primary venues (in order of record strength):

1. **`active/<id>/MANIFEST.md` → Review log**
   Binding dispositions (`accepted`, `changes_requested`). Required for state transitions.

2. **`active/<id>/DEBATE.md`** (optional but preferred for long threads)
   Free-form argument, alternatives, dissent. Not binding until summarized into Review log.

3. **GitHub PR conversation** on PRs that `Implements: <ITEM-ID>`
   Implementation debate. Critical unresolved threads **block merge**, not necessarily proposal close.

4. **GitHub issue** linked from MANIFEST (optional tracking issue)
   Cross-cutting or multi-PR discussion.

5. **Chat / agent transcripts**
   Ephemeral unless an agent **posts a summary** into Review log or DEBATE.md.
   *Unposted chat is not consensus.*

**Rule:** If it is not in MANIFEST Review log, DEBATE.md, or a linked PR/issue, it did not happen for process purposes.

---

## Consensus mechanics (by item priority)

Consensus is **item-scoped**, not only proposal-scoped. A proposal may be `executing` while some items remain `todo`.

| Item priority | To mark item `done` | To mark item `wontfix` | To start item (`doing`) |
|---------------|---------------------|-------------------------|-------------------------|
| **P0** (security, gates, credential containment) | ≥1 Reviewer **accepted** on the *item or PR* + Executor evidence + gates green | Author **or** Reviewer + written reason in ITEMS/Review log; Operator if history/credentials | After proposal `accepted` **or** explicit Reviewer OK on that item |
| **P1** (SSOT, providers, DeepForge fixes) | Executor evidence + gates green; Reviewer silence after 1 clear PR comment cycle is OK | Reviewer or Author | proposal `accepted`/`executing` |
| **P2–P3** | Executor evidence | Executor or Author | proposal `posted`+ is enough |

**Proposal-level `accepted`:**

- At least **one non-author Reviewer** with `status: accepted` in MANIFEST, **or**
- Author is Operator and explicitly self-accepts for solo-maintainer mode (record in Review log).

**Dissent:**

- `changes_requested` from a Reviewer on a **P0 item** blocks that item until resolved or escalated to Operator.
- Dissent on P2 does not block other items.

**No supermajority theater:** one clear Reviewer + evidence is enough except Operator-only steps (credentials, force-push).

---

## Rules for **closing** a proposal

A proposal may move to `closed` when **all** of the following hold:

### A. Item terminality

Every row in `ITEMS.md` is one of: `done` | `wontfix` | `blocked` with **Operator-owned** permanent deferral noted.

- Prefer **zero** `blocked` at close. If unavoidable, close as `closed` with `outcome: partial` and list residual blocks in MANIFEST.

### B. Review record

- MANIFEST Review log contains final disposition: `closed-complete` | `closed-rejected` | `closed-superseded` | `closed-partial`.
- `registry.yaml` status set to `closed` and `closed_at` set.

### C. Mechanical move

```text
docs/proposals/active/<id>/  →  docs/proposals/closed/<id>/
```

Commit message: `proposal(<id>): close (<outcome>)`

### D. Who may close

| Outcome | Who may close |
|---------|----------------|
| `closed-complete` | Closer = Reviewer or Author after A+B |
| `closed-rejected` | Author, or Reviewer with Author ack in log |
| `closed-superseded` | Registrar/Reviewer citing superseding proposal id |
| `closed-partial` | Reviewer + note of residual Operator items |

**Executors alone may not close P0 proposals** that still have open security items (e.g. CE-13 history remediation) without Operator note in Review log.

### E. Rejection path

Proposal can be closed without executing items if Review log states rejection rationale and ITEMS are all `wontfix`.

---

## Itemization rules (ITEMS.md)

| ID | Claim / work | Priority | Owner | Status | Evidence |
|----|--------------|----------|-------|--------|----------|
| CE-01 | … | P0 | grok-archw1z | done | commit/PR |

Statuses: `todo` | `doing` | `done` | `blocked` | `wontfix`

Agents **must not** invent work outside ITEMS without adding a row first.

---

## Review posting protocol

1. Registrar: `active/<id>/` + registry (`posted`).
2. Reviewers: MANIFEST `reviewers[]` + Review log.
3. Consensus → `accepted` → Executor PRs → `master-staging`.
4. PR body: `Implements: <ITEM-ID>` (multiple OK).
5. Close per rules above.

---

## Gate coupling

Merges that execute proposal items require:

1. `repo-gate` green
2. `termux-smoke` green
3. Item IDs cited
4. No unresolved **critical** PR review threads

Promotion to `master` follows the same gates once `master-staging` is healthy.

---

## Agent entrypoint

```text
1. Read AGENTS.md (root) then docs/proposals/registry.yaml
2. Pick highest-priority accepted/executing item with status todo
3. Branch off master-staging
4. PR → master-staging with Implements: <ITEM-ID>
5. Update ITEMS.md + registry in same PR when possible
6. Never close P0 security items without Operator evidence
```
