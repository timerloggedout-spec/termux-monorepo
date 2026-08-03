# Consensus (ArchW1z)

How multi-agent decisions become shared truth — and when **no vote** is required.

Related: `docs/proposals/PROCESS.md` · `docs/PR-SUMMARY-PROCESS.md` · `AGENTS.md` · `docs/ARCHW1Z-GATE.md`

---

## Tier summary (read this first)

```text
Tier 0  MERIT        Branch, implement, run gates — no social vote
Tier 1  DRIVER       P2–P3 claims: driver + evidence in the log
Tier 2  LIGHT        P1: driver + evidence; 1 review cycle then silence OK
Tier 3  QUORUM       P0 claims / P0 PR body: driver + distinct second mind OR Operator
Tier 4  OPERATOR     Credentials, force-push, history rewrite — human only
Tier R  RAFT-STRICT  Optional profile for named irreversible subjects (see §5)
```

| Tier | Name | Needs vote? | Commit when |
|------|------|-------------|-------------|
| **0** | Merit | No | Gates/tests green on a branch; exploration allowed to fail |
| **1** | Driver | Minimal | Driver posts evidence; silence OK |
| **2** | Light | Soft | Driver + evidence; after one clear ask, silence ≈ no objection |
| **3** | Quorum | Yes | Driver + ≥1 other Reviewer **or** Operator |
| **4** | Operator | N/A | Explicit Operator comment; agents cannot majority this |
| **R** | Raft-strict | Yes (formal) | Term + single driver + majority of fixed voter set + log commit |

**Default path for code:** Tier 0 → open PR → Tier 1–2 disposition → merge when gates green.  
**Default path for irreversible security claims:** Tier 3–4 (optionally R).

---

## 1. Three paths (not one protocol)

### A. Merit path (preferred for code)

Skip social consensus. Prove accuracy on a branch:

1. Branch from `master-staging`
2. Implement
3. `python3 scripts/ci/repo_gate.py` / `termux_smoke.py`
4. Open PR with honest Status
5. Land when checks green and disposition ≠ 🔴

**Merit answers “does it work?”** Votes do not replace gates.

### B. Social path (claims & sequencing)

Used when asserting shared process truth: proposal accepted/closed, P0 “done”, disposition Status, summary of security scope.

**Home for intent decisions:** `docs/proposals/` (MANIFEST Review log + registry).  
**Projection for landing:** PR body Status + comments.

### C. Authority path (Operator)

Credential rotation, history rewrite, force-push, App permission changes. Not subject to agent majority.

---

## 2. Where decisions live

| Decision type | Primary log | Model |
|---------------|-------------|--------|
| Proposal accept / item done / close | MANIFEST + `registry.yaml` | Social tiers 1–4 |
| PR disposition / summary | PR comment + body + `PR-SUMMARY-LOG.md` | Thin projection of tiers |
| Code correctness | CI checks + branch commits | Merit (Tier 0) |
| Irreversible git history | Operator comment on issue/PR | Tier 4 (+ optional R) |

Proposals own **what we intend**. Branches own **what we measured**. Consensus attaches to **claims**, not to **existence of a branch**.

---

## 3. Ballot labels (social path)

```text
VOTE: accept      — support commit of the proposed decision
VOTE: reject      — block; state reason
VOTE: abstain     — present; not counting toward quorum
VOTE: summary OK  — ack for P0 PR body rewrite only
```

One vote per voter id per **term**. Log entry required — unposted chat does not count.

**Terms:** `subject-id/n` (e.g. `pr-3/summary/2`, `ce-13/history-rewrite/1`). One driver per term; conflicts open `n+1`.

---

## 4. Subject → tier map

| Subject | Tier |
|---------|------|
| Create branch / push experiments | **0** |
| P2–P3 item `done` | **1** |
| P1 item / ordinary PR disposition | **2** |
| Proposal `accepted` (non-author review) | **3** (or Operator self-accept logged) |
| P0 item `done`, P0 PR body rewrite | **3** |
| Merge to `master-staging` | **0 checks** + disposition not 🔴 |
| Promote to `master` | **0 checks** + may require Operator |
| Force-push / history rewrite / credential rotation | **4** |
| Optional formal close of high-stakes proposal | **R** if enabled for that subject |

---

## 5. Raft as an **optional strict profile** (not the default model)

Raft was considered as a real consensus design, not decoration.

**Keep if using profile R on a named subject:**

- Single driver (leader) per term  
- Monotonic terms; ignore stale term votes  
- Majority of a **fixed voter set** declared in the term open  
- Decision committed only in the append-only log  

**Do not use Raft as the global control plane:** membership churn (agents offline), unequal authority (Operator ≠ peer), and multi-subject concurrency make a single cluster Raft a poor fit. Per-subject Tier 3 already captures most of the value.

Enable R by naming it in the term open: `profile: raft-strict voters: [operator, grok-archw1z, devin]`.

---

## 6. CRDT merge strategies (investigation & recommendations)

CRDTs converge concurrent updates **without** voting. Use them for **state that should merge**, not for **authorization**.

### Strategy cheat sheet

| Strategy | Behavior | Use here | Avoid for |
|----------|----------|----------|-----------|
| **G-Set** | Add-only; merge = union | Observed bot findings, “seen commit SHAs” | Anything that must be revoked cleanly |
| **OR-Set** (observed-remove) | Add/remove with unique tags; concurrent add∥remove keeps add if not observed | Agent roster membership, label sets, item id sets | Security “credential rotated” flags |
| **2P-Set** | Remove wins forever | Tombstones for deleted paths in indexes | Re-adding same id after remove |
| **LWW-Register** | Highest timestamp wins | Non-critical UI prefs, last smoke run timestamp | Disposition Status, proposal state |
| **LWW-Element-Set** | Per-element timestamps | Soft metadata | P0 claims |
| **MV-Register** | Keep all concurrent values | Surface conflicts for a human/agent to pick | Silent auto-resolve of Status |
| **G/PN-Counter** | Merge by max per replica | Ratchet debt counters (aligns with repo-gate baseline) | Voting tallies as authority |
| **RGA / sequence CRDTs** | Concurrent text edit | Collaborative DEBATE.md drafts (optional) | MANIFEST binding outcomes |
| **Three-way / MRDT (Git-like)** | LCA + two tips → typed merge | Branch merges, registry field merges with explicit rules | Pretending merge = approved claim |

### Recommended bindings for this monorepo

| Data | Merge strategy |
|------|----------------|
| **Git branches / commits** | Git’s own history (three-way merge + gates) — already merit path |
| **`registry.yaml` item rows** | Field-level: `status` is **not** LWW — requires Tier 1–3 social commit; `evidence` links are G-Set (union) |
| **PR-SUMMARY-LOG** | Append-only G-Set of rows (never rewrite history of the log) |
| **Review log entries** | Append-only; concurrent reviews = union (OR-Set of note ids) |
| **Disposition Status (🟢🟡🔴⚪)** | **Single-value register under social tier** — concurrent Status → MV-Register until Tier 2–3 resolves (do **not** LWW) |
| **repo-gate baseline counters** | Ratchet = min/monotonic decrease only (domain-specific; not classic PN-Counter up) |
| **Session SSOT / agent memory** (future) | OR-Set + confidence-LWW for soft memories; **never** CRDT-merge secrets into git |
| **DEBATE.md** | Optional RGA/LWW for prose; binding outcome still copied into Review log via vote |

### Rule of thumb

```text
CRDT  →  concurrent facts that should converge without a meeting
Vote  →  authorization to treat something as shared institutional truth
Gate  →  mechanical proof about a concrete revision
```

LWW is the wrong default for **Status** and **proposal state**: wall-clock or agent-local clocks race; security claims must not flip because a slower agent wrote later.

---

## 7. PR summary anti-monopoly (distinct PRs)

Three consecutive = **three different PR numbers**. Iterating the same PR is always OK. Details: `docs/PR-SUMMARY-PROCESS.md`.

---

## 8. Bots

Bots (Devin, CodeRabbit, ecc-tools, …) emit **evidence**. They are not voters until a roster agent posts `VOTE: accept` on a specific finding into the log. See earlier triage map in git history / `PR-SUMMARY-PROCESS.md` for tooling options.

---

## 9. Quick reference

```text
Explore on a branch          → Tier 0 (no vote)
Claim “P2 done”              → Tier 1
Claim “P1 ready to merge”    → Tier 2 + gates
Claim “P0 / security done”   → Tier 3
Rotate keys / rewrite history → Tier 4
Optional formal subject      → profile raft-strict
Merge concurrent facts       → CRDT (OR-Set / G-Set / counters)
Merge authority              → never CRDT; use tiers
```
