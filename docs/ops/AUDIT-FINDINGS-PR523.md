# Independent Audit Findings — PR #523 (Phase A–E validation + historical backfill stall audit)

**Auditor:** Tanka collaborator session (parallel to the primary author/agent working PR #523)
**Scope requested:** Independently validate Phases A–E on current head, focusing on Phase B (emit) and Phase C (correlate) concrete implementation gaps; audit `context relationship historical backfill` run history for admission / queue / execution / effect / pagination stalls; preserve evidence identity (run_id + attempt + head_sha + ref + observed state); no merge/force-push/delete/close/credential rotation; no weakening of quality gates.

**Evidence pinning note:** PR #523 received live commits from another contributor/agent while this audit was in progress — head moved from `25bff014c37210289fc297903add16c09ef859c6` to `bb8586f28f943f3f974872388573edc7d873b91f` (43 → 44 commits) during the review window. Every file-level finding below was re-verified against the blob SHA at the newer head; all files discussed were byte-identical across both commits except for the addition of `.github/workflows/historical-backfill-promotion-gate.yml`, which is reviewed separately in Finding 6. All findings are therefore valid as of head `bb8586f28f943f3f974872388573edc7d873b91f` on ref `ops/automate-historical-backfill-ates-she`.

---

## Finding 1 — Phase A (Measure): implementation matches the "IMPLEMENTED / VALIDATED" claim

`she/metrics/agent_throughput.py` (blob `723bc6fad148aa12ccd8ce9fc72d39e065098d32`) is a pure, network-free reducer. Verified directly against source:

- Missing-evidence handling is real, not decorative: `wtcv_per_min` is `None` whenever even one completed task lacks a complexity value (line-level check: `len(known_complexities) == len(completed)`), and `parallel_yield`/`ates` are `None` unless an explicit `sequential_baseline_sec` is supplied — the reducer never invents a baseline from the observed run.
- The documentation gate `scripts/ci/verify_agent_quality.py` genuinely enforces what it claims: module docstring presence, docstrings on all public symbols, presence of two specific explanatory comments (`# Sequential baseline is only valid when…`, `# Keep throughput observational…`), and a hard `require("MIN_ATES_THRESHOLD" not in source, …)` check that stops anyone from quietly turning ATES into a speed-only merge gate. This is a real, non-decorative gate — confirmed by reading the assertions, not just their docstrings.
- `tests/test_she_agent_throughput.py` exists and is wired into both `agent-quality-lane.yml` (`python -m unittest tests.test_she_agent_throughput -v`) and is importable (`from she.metrics.agent_throughput import ThroughputMetrics, reduce_events`).

**Minor nit (not a gate weakening, not blocking):** `agents=len(agents) or 1` in `reduce_events()` silently substitutes `1` when no event carries an `agent_id`. Every other missing-evidence path in this file deliberately returns `None` rather than a manufactured number (that's the file's own stated design principle in its docstrings). This one field is the exception — a run with zero identifiable agents is reported as "1 agent" rather than as evidence-absent. Recommend either an explicit `None`/sentinel here too, or a source comment explaining why `agents` is treated differently from every other metric in the same reducer.

**Verdict:** Phase A's claim is accurate. No doc/code mismatch found.

---

## Finding 2 — Phase B (Emit): no code exists yet; docs do NOT overclaim

Searched the full PR diff and the current tree for any workflow or script that actually emits a Phase-B telemetry event (JSONL receipt with run/attempt/SHA linkage) during a real workflow run. None exists. What exists is:

- `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json` — the event **shape** (a contract), not an emitter.
- `docs/ops/AGENT-THROUGHPUT-METRICS.md` and `docs/ops/AGENTIC-INTEGRATION-PLAN-STATUS.md` — both explicitly say Phase B is "STARTED" and that "the next implementation increment wires eligible agent workflows to emit these receipts" — i.e., the docs themselves say this is not built yet.

No workflow file in the PR (`agent-quality-lane.yml`, `agent-runtime-stall-watch.yml`, `context-relationship-backfill.yml`, `context-relationship-backfill-watcher.yml`, `historical-backfill-promotion-gate.yml`) writes an agent-throughput JSONL event anywhere.

**Verdict:** Phase B's own "STARTED" (not "implemented") label is accurate. This is the opposite of a documentation/code mismatch — the docs are correctly conservative here. No gap to close in this PR; the gap is simply future, undone work, honestly labeled as such.

---

## Finding 3 — Phase C (Correlate): same pattern as Phase B — contract only, honestly labeled

Grepped the full diff for "correlat" and "Phase C": every occurrence describes a **target** ("Actions run/attempt + SHA + PR/review + Action→Effect + corpus observation + environment evidence") or says "the correlation target is now explicit" — never a working correlator. No code joins run evidence to PR review evidence to corpus observation anywhere in this diff.

**Verdict:** Matches the "STARTED / CONTRACT DEFINED" label. No overclaim found.

**Net finding across 2 and 3:** the request asked us to hunt for "concrete implementation gaps, not just documentation" on Phases B/C specifically — the actual gap is the inverse of what's usually suspicious: there is no code at all yet for either phase, and the docs already say so plainly. The real risk to flag isn't a doc/code mismatch on B/C themselves, but making sure nobody later reads "STARTED" as "done" — the wording is precise today; it should stay that way as Phase B work actually lands.

---

## Finding 4 — Runtime stall taxonomy: the docs claim six stall classes; the code implements two

`docs/ops/AGENTIC-INTEGRATION-PLAN-STATUS.md` states: *"Current diagnostic classes include: admission stall; queue stall; execution/heartbeat stall; effect stall; pagination stall; routing loop."*

Reading the actual watcher implementations end to end:

- **`agent-runtime-stall-watch.yml`** (blob `73158334471b0f1d38bc48402ec847cd709973be`) only classifies two states: `QUEUE_STALL_CANDIDATE` (queued run older than 20 min) and `EXECUTION_STALL_CANDIDATE` (in-progress run older than 45 min). It pulls exactly two API views: `status=queued` and `status=in_progress`. There is no code path that produces an `ADMISSION_STALL`, `EFFECT_STALL`, `PAGINATION_STALL`, or `ROUTING_LOOP` classification anywhere in this file.
- **`context-relationship-backfill-watcher.yml`** is a `workflow_run`-triggered observer scoped to `types: [requested, in_progress, completed]` for the one named workflow. It records job/step/artifact state faithfully (including `run_id`, `run_attempt`, `head_sha`, `head_branch` — good evidence identity practice) but it is purely **reactive**: it only produces an observation when the watched workflow is *requested* at all.
- **Pagination stall is handled, but not as a classified observation** — it's enforced as a hard `raise SystemExit('next_start_page did not advance...')` inside `context-relationship-backfill.yml` itself (see Finding 5). That's a real, working check, but it surfaces to a maintainer as an ordinary red CI run, not as a labeled `PAGINATION_STALL` artifact the way queue/execution stalls are labeled. Someone scanning Actions history for stall patterns specifically would not see it tagged as such.
- **Admission stall has no detector anywhere.** Nothing in this PR (or in the repository, as far as this audit found) can express "a workflow was supposed to run on a schedule and never even got queued." Both watchers above start from "there is a run to look at." A workflow that never gets a single run in its lifetime is invisible to both of them by construction.

**Verdict:** This is the concrete implementation gap the task asked us to find. 2 of 6 documented stall classes are actually detected and classified; pagination stalls are caught but not labeled as such; admission stalls (arguably the most severe class, since it means the automation never ran at all) have no detection mechanism in this PR.

---

## Finding 5 — Live backfill audit: the corpus is stuck due to an admission stall, not a pagination stall — with hard evidence

Applying the WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD loop against the actual `context relationship historical backfill` workflow on `master` (workflow id `337520624`, path `.github/workflows/context-relationship-backfill.yml`):

- **RE-FETCH:** `GET /repos/timerloggedout-spec/termux-monorepo/actions/workflows/337520624/runs` → `"total_count": 0`. This workflow has **never executed, ever**, on `master`.
- **COMPARE (why):** the version of this file currently live on `master` (blob differs from the PR's version — diffed directly) has **no schedule trigger at all** — only `workflow_dispatch` requiring a manually-supplied `history_start_page` input — and it targets/pushes to `master-staging`, not `master`. It has simply never been manually invoked.
- **VALIDATE against the canonical manifest:** `workspace/llm_map/context_relationships/manifest.json` on `master` shows `history_window.next_start_page: 2`, `latest_observed_at: 2026-08-19T07:53:15Z`, and `default_branch: "master-staging"` (a stale field, itself evidence nothing has touched this manifest since). Commit history on that exact file shows exactly two commits, both on 2026-08-19, both `chore(context): refresh relationship index` (an initial-build commit message, not a "continue backfill" one) — i.e., the corpus was built once and never continued.
- **On `master-staging`** (the branch the live workflow actually targets): manifest there shows `next_start_page: 2` also, but `latest_observed_at: 2026-09-07T12:33:24Z` — so `master-staging` did receive at least one manual continuation run after the initial build, and it is *also* still incomplete.
- **CLASSIFY:** by the stall rule given in the task ("a run that completes without advancing `next_start_page` must be classified as pagination stall") — `master`'s workflow doesn't qualify as a pagination stall, because it has **zero completed runs to evaluate**; this is an **admission stall** (the more severe, prior-order class — the automation was never triggered in the first place, so it never got the chance to stall on pagination). `master-staging`'s workflow did run at least once (partial completion) but remains incomplete as of the most recent observation — that segment is consistent with ongoing (if infrequent) manual continuation, not a hard stall, since there's no record of a *completed* run on `master-staging` failing to advance either (no run history was retrievable for a `master-staging`-scoped workflow via the API in this session — the audit could not fully re-fetch that workflow's own run log to confirm whether its historical runs advanced cleanly or stalled; **this remains an open sub-question, flagged rather than guessed at**).
- **RECORD (evidence identity):**
  - Workflow: `context relationship historical backfill`, id `337520624`, path `.github/workflows/context-relationship-backfill.yml`, ref `master`, run count: **0**.
  - Manifest observed state (ref `master`): `next_start_page=2`, `latest_observed_at=2026-08-19T07:53:15Z`, `default_branch="master-staging"` (stale).
  - Manifest observed state (ref `master-staging`): `next_start_page=2`, `latest_observed_at=2026-09-07T12:33:24Z`.
  - PR #523 head at time of this finding: `bb8586f28f943f3f974872388573edc7d873b91f`.

**Verdict:** PR #523's own narrative ("this is currently a promotion/runtime sequencing issue, not an unexplained collector stall") is correct and matches the hard evidence — but the more precise classification is **admission stall on `master`**, not merely "not yet promoted." The distinction matters for the taxonomy in Finding 4: this exact situation is the one the current watcher tooling cannot detect on its own (see Finding 4) — it took a direct `total_count: 0` check against the Actions API to surface it, not the watcher artifacts.

---

## Finding 6 — New commit added during this audit: `historical-backfill-promotion-gate.yml` — verified sound, not a gap

While this audit was in progress, the PR branch gained one new file: `.github/workflows/historical-backfill-promotion-gate.yml`. It runs on `pull_request` (`opened, synchronize, reopened`) and reads `master-staging`'s manifest directly, hard-failing the PR check if `next_start_page` is not `null`:

```
if nxt is not None:
    raise SystemExit('PROMOTION BLOCKED: current master-staging historical backfill is not complete; ...')
```

Independently re-fetched `master-staging`'s manifest for this audit (see Finding 5): `next_start_page = 2`, not `null`. **This gate would correctly fail/block right now if evaluated against the live state** — which is exactly the intended behavior. This is a real, working safety gate added in direct response to the sequencing risk described in the plan doc, and it does not weaken anything. No action needed; noted for completeness of the evidence trail since it landed mid-audit.

---

## Finding 7 — Constraint compliance statement

No merge, force-push, delete, close, or credential-rotation action was taken against PR #523 or any branch in this repository during this audit. No existing quality gate was modified, loosened, or bypassed. This document is being delivered as a new file on a separate branch/PR explicitly linked to PR #523, per the instruction to return findings as reviewable changes rather than chat-only summary, and to avoid pushing directly onto a branch that was under active concurrent edits during the audit window (see the evidence-pinning note above).

---

## Summary for reviewers

| Area | Claim | Verified state | Gap? |
|---|---|---|---|
| Phase A (Measure) | IMPLEMENTED / VALIDATED | Confirmed accurate; one minor nit (`agents` defaulting) | No (nit only) |
| Phase B (Emit) | STARTED | Confirmed: contract only, no emitter code, docs already say so | No (accurately labeled) |
| Phase C (Correlate) | STARTED / CONTRACT DEFINED | Confirmed: target defined, no correlator code, docs already say so | No (accurately labeled) |
| Stall taxonomy (6 classes documented) | "Current diagnostic classes include…" | Only 2 of 6 (queue, execution) are actually classified in code; pagination stall is caught but unlabeled; admission stall is undetectable by current tooling | **Yes — concrete gap** |
| `master`'s historical backfill | "still on page 2" | Confirmed: 0 runs ever, admission stall, not pagination stall — corpus frozen since 2026-08-19 | **Yes — concrete, evidenced gap** |
| New promotion gate | (added mid-audit) | Verified correct: would block promotion right now given real `master-staging` state | No — working as intended |

**Recommended next increments (not implemented here, per the no-merge/no-new-automation-decision constraint of this audit):** (1) extend `agent-runtime-stall-watch.yml` or a sibling workflow to also detect admission stalls, e.g. by comparing each scheduled workflow's `cron` expectation against its actual last-run timestamp; (2) have the pagination-stall failure in `context-relationship-backfill.yml` also emit a labeled artifact/observation (not just a red CI run) so it's visible in the same evidence stream as queue/execution stalls; (3) once promoted, confirm via a fresh `RE-FETCH` that `master`'s backfill workflow actually gets its first scheduled run and that `next_start_page` genuinely advances past 2 — this audit found no reason to doubt the mechanism will work, only that it has not yet been observed running.