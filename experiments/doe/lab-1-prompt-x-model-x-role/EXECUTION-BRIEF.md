# lab-1 — EXECUTION BRIEF (go/no-go)

`[MUSEai]@{role:{doe-mgr-control-suites}}` · Oversight:
`doe-expert (44bb4068)` · Campaign:
`experiments/doe/lab-1-prompt-x-model-x-role/` · Date: 2026-10-31

## Verdict: NO-GO (defer — no named live anchor)

Per doctrine (owner, 2026-10-31): controls calibrate, live
decides; a control earns execution **only** as a calibration
anchor for a **named** live campaign. No current live campaign's
primary response is anchored by lab-1 (per-campaign audit §3).
Execution therefore stays ∅ until doe-expert names an anchor
campaign AND the recheck gate (§5) passes. Independent
blocker already present: target-doc drift (§4 R2, 1/15
fragments missing @master). This is a defer,
not a kill: DESIGN + PLAN stay admitted, byte-stable, ready.

## 1. What lab-1 is (verified @master)

- Control suite, `suite_type: control`, status
  `admitted_design_only`, 0 dispatched.
- Design: 2×2×2 full factorial — prompt {prompt-a
  strict-verbatim, prompt-b loose} × model
  {openrouter/openai/gpt-4o-mini,
  openrouter/meta-llama/llama-3.1-8b-instruct:free} × role
  {triage, reviewer}; 8 tasks inherited verbatim from pilot-1;
  temp 0; context = explicit full target document; routing
  fixed icm-guided (pilot-1 winning levels).
- PLAN.json: 64 runs / 8 cells / 8 distinct instance_keys;
  file sha256 `295c075c427a…` @master; byte-identical across
  all wiring PRs (#2669 build, #2674 phrases wiring).
- Selection rule (pre-registered): top cell ≥ 0.80 accuracy
  ∧ margin ≥ 0.05, else `no_selection`.
- `provider_phrases: {}` — NOT ESTABLISHED for both routes
  (established sets are DeepSeek-shaped only).
- `scripts/doe/lab_runner.py` never dispatches (plan/record
  only). **No dispatch route is named in DESIGN** beyond
  "fleet provider lanes" — an execution route must be named
  before any GO (gap G1).
- Anchor baseline (pilot-1, executed, 32 rec): verdict
  `threshold_not_met`; effects routing +0.06, representation
  −0.56, interaction −0.06; compressed level BANNED from live
  until fragment-preserving. Lab-1 fixes pilot-1's winning
  levels, so its read is LLM prompt/model/role on the same
  tasks — not a re-run of pilot-1's question.

## 2. Quota cost (est.)

| Item | Cost |
|---|---|
| llama :free arm | 32 runs vs OpenRouter free-model daily cap (registry: 20/min; daily cap tiered by credits purchased — 50/day if < $10 purchased, 1,000/day if ≥ $10). 32 runs = 64% of a 50/day window, shared with every other free-route consumer (e.g. DeepSeek OpenRouter reroute). Must be scheduled against `GET /api/v1/key` `free_model_daily_requests.remaining`. |
| gpt-4o-mini arm | **NOT a `:free` route.** DESIGN's "free routes only / zero paid quota" note conflicts with its own model factor: 32 runs on a paid model. Dollar cost is micro (≈1–2k input tok/run per pilot-1 explicit means ~1,052 tok + prompt/role overhead; ~64k input + small output total ⇒ ≈ $0.01–0.05 at gpt-4o-mini list) but it (a) spends funded `OPENROUTER_API_KEY` balance, (b) violates the free-only constraint as written. GO requires resolving this first: amend model level to a `:free` variant (⇒ new PLAN = new cohort) ∨ doe-expert records an explicit micro-spend waiver. |
| PAT / Actions | Brief + records PRs via PAT helper: ~8 core calls/PR (preflight-derived reserve, `pat_publish.py`). If execution rides an Actions workflow: 1 dispatch + run minutes for 64 short calls — NOT ESTABLISHED until the dispatch route is named (G1); no Actions estimate is claimed before then. |
| Plan/record | Offline-deterministic, zero quota (verified in runner docstring + DESIGN). |

Net: quota is **not** the blocker. Cost is small; the
free-route conflict and the missing dispatch route are
process blockers, and §3 is the substantive blocker.

## 3. Calibration value per live campaign (audit)

| Live campaign | Its primary response | Does lab-1 anchor it? |
|---|---|---|
| Dispatch framing — work-order name "live-1 framing"; landed in repo as **live-4-dispatch-framing** (PR #2802, `admitted_design_only`, owned by doe-mgr-live-builds) | Rework-free first-pass merge of Jules dispatches under framing {a = DO pattern A only, ba = B≫A}, blocked by Nov wave (D2 2026-11-03, D4 >11-08, M2/M3 gated); rule ≥12 dispatches ∧ Δ≥0.20 ∧ no block reversal | **NO.** Different arm (Jules, not OpenRouter), different task class (builds, not fragment recovery), different factor (dispatch framing, not strict/loose extraction prompt), different primary response. Lab-1's prompt effect is at most a weak directional prior; it calibrates no live-4 response, threshold, or selection rule. |
| live-2-prlane-tuning (in repo, phase 0 PASS_WITH_RECORDED_GAP) | Outcome-consistency of a **deterministic** classifier replayed over frozen snapshots | **NO.** ∅ LLM runs in live-2; ∅ shared units, responses, or thresholds. (Name collision only: lab-1's `triage` is a prompt role line, not the pr-lane classifier — steward CHECK, PR #2789.) |
| live-3 phrases — **live-3-phrases-deepseek** (in repo; supersedes live-3-phrases-jit PR #2799, whose DESIGN is `superseded` on master) | `findings_actioned_rate` on live DeepSeek invoke/review dispatches under placement × form × selection (18 cells + unphrased control); adopt rule Δ≥0.10 @ n≥20 | **NO.** Lab-1 declares `provider_phrases: {}` for its routes — by design it contains no phrase treatment, so it cannot calibrate phrased-vs-unphrased effects, placement, or form levels. Its unphrased OpenRouter cells are not live-3's control (different provider, host surface, tasks, response). |
| fb-pages-mvt-1 (live, executing; verdict ≤ 2026-11-10) | Attributed redemptions/cell for FB copy angles | **NO.** ∅ shared factor, response, or surface. |
| speculators/token-strategies (design-only, GPU) | Lossless-gated speedup/acceptance on GPU lanes | **NO** — and it is itself design-only, not a live anchor consumer. Its gate (≥30 pairs powered per owner pack; lossless HF-verify) is independent of lab-1. |

**What lab-1 *would* anchor, if one is named:** the first LLM
baseline on pilot-1's exact 8 fragment-recovery tasks —
whether any prompt×model×role cell clears the pre-registered
0.80/0.05 rule for OpenRouter fragment-extraction work
(triage/reviewer-shaped). That becomes a real anchor the
moment a live campaign proposes to use these routes for
fragment recovery. None currently does.

## 4. Risks

- **R1 Route drift since PLAN pin.** Base sha `3b7fa32b`
  (2026-10-30). OpenRouter model strings are unpinned
  aliases: `openai/gpt-4o-mini` carries no dated snapshot,
  and `:free` endpoints change underlying providers /
  availability without notice. Instance_key covers
  provider + model string + prompt/tools hashes + role —
  **not** upstream snapshot or endpoint. A 2026-11 execution
  may not be the instance the PLAN names.
- **R2 Target-document drift.** Tasks score verbatim
  fragments against in-repo target docs; those docs evolve
  on master. DESIGN fixes "explicit full target document"
  without pinning its revision. Fragments missing at
  execution-time master would floor accuracy artifactually
  (a harness artifact, not a model effect). **Already
  real, verified at brief time (2026-10-31):** 14/15
  required fragments found verbatim @master; 1 MISSING —
  t6 fragment `MUST use observed dispatch rate`
  (target `docs/proposals/active/doe-live-method-competition/PROPOSAL.md`).
  Executing today would cap t6 at 0.5 accuracy in every
  cell for a non-model reason. The check must re-run at
  execution time, or context must be pinned to base-sha
  document revisions by amendment.
- **R3 Free-cap contention.** 32 `:free` runs in one window
  can starve same-day free-route live work (see §2). Execute
  only in a window whose remaining free cap ≥ 64 + reserve.
- **R4 Power.** 8 tasks/cell, one obs per cell per task:
  margins near the 0.05 rule are within noise of a single
  task flip (1 task = 0.125 of a cell mean on binary-ish
  scoring; fragment-fraction scoring softens but does not
  remove this). A `selection` verdict from 64 runs is a
  calibration read, never a production ruling — consistent
  with control status.
- **R5 Dispatch-route invention.** Because no route is
  named (G1), an executor improvising one (e.g. direct API
  script) would create an unstamped, unrepeatable cohort.
  GO must name the route + its stamp fields first.

## 5. Recheck method (pre-execution gate; all must pass)

1. **Model availability:** `scripts/openrouter_free_catalog.py`
   / `GET https://openrouter.ai/api/v1/models` — both model
   IDs present; record pricing entry for gpt-4o-mini and
   `:free` flag for llama; record any successor/snapshot IDs.
2. **Free cap:** `GET /api/v1/key` →
   `free_model_daily_requests {used, limit, remaining}`;
   require remaining ≥ 64 at dispatch window start.
3. **Fragment presence:** grep every `required_fragments`
   entry in its target doc @execution master; any MISS ⇒
   pin context to base-sha revisions by amendment or stop.
4. **PLAN stability:** re-run `lab_runner.py plan` in a
   scratch copy; PLAN.json must be byte-identical
   (sha256 `295c075c427a…`). Any diff ⇒ new cohort, new
   brief — not lab-1 execution.
5. **Smoke:** 1 run per model (2 runs, counted against the
   same caps) returning scorable output before the 64.
6. **Route naming:** doe-expert names the dispatch route
   (G1) + the anchor campaign (§3) in the GO ruling.

## 6. Ruling requested

**NO-GO now.** Re-trigger this brief when (a) a named live
campaign needs the OpenRouter fragment-recovery baseline,
(b) the gpt-4o-mini free-route conflict is resolved
(amendment ∨ waiver), and (c) §5 passes at execution time.
Until then: lab-1 stays `admitted_design_only`, 0 dispatched,
∅ self-dispatch by this lane.

---
Evidence: DESIGN.json / PLAN.json / README @master (this
campaign dir); pilot-1 SUMMARY.json; live-2 + live-3 (jit + deepseek) + live-4
DESIGN.json @master; DOE-RECON-2026-10-31.md (conclusions
2+4, as errata-corrected); quota registry `openrouter.*`
rows; PRs #2669 / #2674 / #2789 / #2794 / #2799 / #2802.
