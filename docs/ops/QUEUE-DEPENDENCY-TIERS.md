# QUEUE DEPENDENCY TIERS — drain in dependency order by construction

Filed by the optimizations-assurance lane, 2026-11-03, as the
structural half of the queue diagnostics (owner's question: *"Are
they queued in best order of dependencies?"* — answer: no; evidence
below).

## ① Evidence — how the queue actually drains

Sampled live at job granularity (job `started_at` vs run
`created_at`, 28 job starts across recently-started runs,
2026-11-03 ~20:5xZ):

- **Waits are tier-blind.** Tier-1 (gates/infra) median job wait
  **37m**; tier-4 (collectors/followers) median **36m**. The
  scheduler does not know what a dependency is.
- **Inversions are real.** 3 cross-tier inversions in the sample:
  e.g. Context Relationship and Sweep Accountability jobs created
  20:14Z started 20:47Z, two minutes BEFORE the repo-gate job
  created 20:10Z (started 20:49Z). A later-created follower beat
  an earlier-created gate to a runner.
- Drain order ≈ **global arrival order at job granularity**,
  perturbed by scheduler jitter, with one local exception: within
  a single workflow the order held FIFO in every sampled family.
- Operationally this already bit once today: the studysprint
  0.2.0 cuts (created 19:42Z) waited ~40 minutes while monorepo
  follower runs spawned and started around them — the two repos
  share one account runner pool.

## Exhibit A — the same class at authoring time

Findings register F-G11: the release-cut EPUB leg shipped into
the ss workflow BEFORE its tree dependency (`export_epub`, PR
#4521) existed, and the 0.2.0 TUI cut fired against a tree
predating it — dependency order violated when the work was
AUTHORED, not just when it drained. One class, two surfaces:
**nothing in the machinery represents "this must land/run after
that."**

## ② The tier model

| Tier | Class | Examples |
|---|---|---|
| 1 | Infrastructure & gates | repo gate, emulator gate, admission, watchdog |
| 2 | Release machinery | release-cut, studysprint-sync, publish-*, submission-snapshot, merge promotion |
| 3 | Builds & proofs | strands proof, cert-project, entry builds |
| 4 | Collectors & followers | ledgers, audits, evidence collectors, feed-collects, comment-router followers |

Machine-readable form: `ops/quota/dispatch-tiers.json`
(schema `queue.dispatch-tiers/v1`, matched by workflow-name
pattern, first match wins, default tier 4).

## ③ Enforcement design (what "by construction" means here)

GitHub exposes **no queue-reorder or priority API** — anyone
promising one is asserting. The fleet's real instruments, in
order of leverage:

1. **Tiered cancel doctrine (proven 2026-11-03).** In a flood,
   cancels take tier 4 first (superseded followers), never tiers
   1–2. Executed today: 350 cancels, 0 of them gates/machines;
   the proof + cuts + sync all completed inside the window.
2. **Inflow hold.** A push/comment hold starves spawn at the
   source; the surviving queue drains in arrival order without
   new tier-4 chains jumping in via `workflow_run`.
3. **Admission-side tiering (the build item).** The dispatch
   admission guard reads the queue-state feed (PR #4621): when
   queued depth exceeds the saturation threshold, tier-4
   event-followers self-defer (their trigger jobs exit as
   *deferred-by-tier* before occupying a runner) while tiers
   1–3 admit normally. Tier stamps ride dispatch records from
   `dispatch-tiers.json`. Owner of the admission surface:
   Cadence; this doc + table are the contract handed over.
4. **Authoring-time rule (exhibit A's fix).** A workflow leg
   that depends on tree content states the dependency in its
   file header and guards on the content's presence (the
   release-cut EPUB conditional is the pattern, landed
   2026-11-03 as a fix; the rule makes it a convention).

## What this does not claim

Tiering bounds the DAMAGE of a flood; it does not reduce spawn.
Spawn reduction is the sibling fix (trigger-level skip
elimination + single-flight followers) and pairs with this doc.
The queue board (PR #4621) is the shared instrument: drain mix
and per-tier waits are readable from its feed once collectors
stamp tiers.

## v2 — intra-tier edges in machinery (owner ruling, 2026-11-03)

v1's honest limit was stated at filing: tier order cannot
express order WITHIN a tier — and D1's chain has exactly such
edges (the v1.0.0 assembly comes after the 0.2.0 releases;
the snapshot comes after the assembly). The owner ruled that
order belongs in machinery, not in the Desk's hand.
`dispatch-tiers.json` is now schema `queue.dispatch-tiers/v2`:

- **`after` (class-level edges).** A tier-2 entry may declare
  `after: [patterns]` — it admits only when its after-classes
  have no incomplete run in the same scope. Of record:
  `submission-snapshot` after `release-cut` (a snapshot captures
  a cut state; it never precedes the cut it captures) ·
  `publish` after `release-cut`.
- **`chains` (per-entry declared shapes).** Ordered stages of
  workflow-pattern nodes; `parallel: true` stages admit
  together; `scope` discriminates same-workflow nodes
  (`release-cut` at `version:0.2.0` ≠ at `version:1.0.0`);
  `unordered` declares the independents and the leaf. The
  d1-studysprint chain is filed verbatim: *gate → cuts ∥ →
  assembly → snapshot*, proof unordered-independent,
  countdowns the leaf.
- **Executor of record, unchanged for tomorrow:** the Desk's
  release-day sequence executes the Nov-4 line by hand
  regardless. v2 lands BEHIND it and is **verified against
  that execution** — the recorded order is replayed against
  the declared chain; any mismatch files as a spec bug or an
  execution deviation, both on record. Machinery earns the
  Desk's hand by matching it first.
