---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo (and similar agentic monorepos). Triggers on priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, or when the operator says continue, BIUDL, or maximize actions. Use for live state pulls, dispositions, small-green extracts, and iterative process improvement documented as skills.
---

# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / operator continuous admin on timerloggedout-spec/termux-monorepo (and similar agentic monorepos).

**Triggers:** priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, "continue", "BIUDL", "maximize actions", full telemetry requests, multi-P0.* handling.

**Canonical doc path (same content):** `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md`

**Complements:** `.agents/skills/review-loop` (evidence-first review sequence), `adaptive-feedback-cycle`, `context-relationship-graph`.

## Posture (non-negotiable)

- **Evidence over anecdote.** Every prioritization must cite live rows, run histories, or committed telemetry artifacts.
- **Full telemetry over isolated canary.** agentic-report is one example from the first row of the performance table — never treat it as the only signal. Correlate *every* row.
- **Quota ≠ run prevention.** Workflow activation (schedule/dispatch + daily AIC guardrail) can succeed while the agent step fails on Copilot/CLI quota. Separate activation success from agent failure.
- **Authority > ranking.** MoneyBall / 3L0 / leaderboard scores are decision-support only. Hard authority, policy, and human gates always dominate.
- **Anti-sprawl.** No source mutation in L0. Prefer thin stacked PRs. No vendoring of upstreams as promotion gates.
- **Multiple P0.** Handle concurrent P0.* classes by fingerprint/classification (workflow-failure, gate-failure, smoke-failure, observe-only for security).

## Primary surfaces

| Surface | URL / path | Use |
|---------|------------|-----|
| Actions performance (UI export) | `/actions/metrics/performance` | Job failure % + avg runtime; export CSV |
| Actions minutes | same page, total-minutes tab | Consumption ranking |
| Workflow runs | `/actions/workflows/<file>` | Per-workflow history |
| SHE | `she/` + `docs/architecture/SELF-HEALING-ENGINE-ROADMAP.md` | P0.1–P0.3 status |
| Telemetry snapshots | `docs/ops/generated/actions-metrics-*-YYYY-MM-DD.csv` | Dated ground truth |
| Collect/reduce CLI | `python -m ops.github_telemetry` | Locally reconstructed metrics |

## Workflow (evidence-led loop)

1. **Pull state** — list open PRs/issues, recent master commits, Actions runs for high-failure workflows, committed CSVs.
2. **Correlate rows** — join job-failures CSV + total-minutes CSV + per-workflow run pages. Rank by (failure_rate × volume) then by authority class.
3. **Disposition** — for each P0 class emit: status, evidence links, next thin increment, authority gate required.
4. **Advance SHE** — only L0 intents that do not mutate source; live token-bearing re-run is the next wire after planner+executor intents.
5. **Leave trail** — commit dated CSVs or correlation notes under `docs/ops/generated/`; update skill if process improved.
6. **No sprawl** — one focused branch/PR per thin slice; squash-merge only after green gates.

When a change is under active review, also run the **review-loop** skill sequence (recon → SHA/run binding → classify findings → smallest fix → re-validate → feed forward).

## P0 classification (current)

| Class | Example signal | L0 target |
|-------|----------------|-----------|
| workflow-failure | agentic-report 100%, continuous-evaluation ~48% | `actions_rerun_failed_jobs` / `actions_rerun_workflow` |
| gate-failure | repo-gate / termux-smoke | `actions_rerun_workflow` / `termux_restart_worker` |
| phase-sync fragility | dependency-phase-project-sync high % | observe + bounded retry |
| security / Dependabot | alerts | `observe_only` |
| high-volume low-failure | peer-review-orchestrator, Jules, Gemini | keep as promotion signals |

## Skill evolution rules

- When operator corrects ("it's a SINGLE EXAMPLE from the first row"), update this skill immediately and commit.
- Prefer reference to live CSVs / API aggregation over re-duplicating numbers in prose.
- Iterative dated CSV snapshots are valuable for time-series; do not delete prior exports.
- Document any new programmatic integration path in `docs/ops/ACTIONS-METRICS-INTEGRATION.md`.
- Derived metrics must be labeled `locally_reconstructed` (no claim of UI Performance Metrics API parity).

## Anti-patterns

- Fixating on one canary workflow while ignoring the rest of the performance table.
- Treating monthly Copilot quota exhaustion as "runs should not fire".
- Ranking purely by failure rate without volume or authority context.
- Opening broad PRs that mix P0.3 live wire with unrelated refactors.

## Retroactive automation-review cadence (added after PR #390 / issue #507)

**Lesson learned:** PR #390 ("docs: formalize category-theoretic notation sets and cross-domain mappings")
ran past 2500 issue comments before anyone flagged it, auto-overflowing into issue #507
("ecc-tools ops: PR #390 /audit"). Root cause (see incident evidence below): `peer-review-orchestrator.yml`
listens on both `pull_request_target: [opened, synchronize, ...]` and `issue_comment: [created]` with no
exclusion for comments it posts itself. Its own `<!-- operator-provider-review:v1 -->` /
`<!-- agent-peer-response-state:v2 -->` state comments (posted under the `github.repository_owner` login,
the default `OPERATOR_EXECUTOR_LOGINS`/`PEER_STATE_PUBLISHER_LOGINS`) satisfy the workflow's own
`relevantEvent` check (`isCurrentProviderRequest` / `isCurrentOperatorAcknowledgement`), so each state
comment is itself a qualifying `issue_comment` event that re-invokes the workflow. Combined with CodeRabbit
hourly rate-limiting (which does not pause the requester), the cycle self-sustained for days at a
~3–10 minute cadence purely from automation talking to automation — not from any human or bot misbehaving
individually.

**Why "wait for the next reactive overflow issue" is not enough:** overflow issues like #507 only fire
*after* the comment ceiling is hit (2500 on this host). By then the loop has usually run for days and the
thread is unreadable. Nothing upstream samples *healthy-looking* recently-merged/closed PRs for the same
self-triggering pattern before it snowballs.

**Proposed lightweight cadence — periodic retroactive automation review:**

1. **Cadence:** run monthly, or after every ~25 merged/closed PRs (whichever comes first) on
   `timerloggedout-spec/termux-monorepo`.
2. **Sample:** pull issue comments + review timelines for a random/recent slice of merged or closed PRs
   (not just open ones — loops can run to completion silently on PRs that eventually merge).
3. **Look for:** comment-count outliers relative to repo baseline, repeat bodies from the same bot/account
   within short (<15 min) windows, and any workflow whose `on:` block includes `issue_comment` /
   `pull_request_review` / `pull_request_review_comment` without an explicit actor/marker exclusion for its
   own posts.
4. **File findings, don't just react:** record each finding as a flagged issue (tag: `automation-misbehavior`)
   citing the workflow file/line and the specific trigger gap, same evidence bar as this incident report —
   file path, line number, and the exact unguarded condition. Route the fix to Operator/Tier-4 (workflow
   edits under `.github/workflows/**` are out of scope for L0/L1 automation itself, matching the
   anti-sprawl posture above).
5. **Track as a P0 class:** add `comment-loop` / `self-trigger` as a recognized signal in the P0
   classification table above once a second occurrence is confirmed, so it graduates from "one-off
   incident" to "known class we actively sample for."

**Incident evidence:** PR #390 (root cause diagnosed read-only, no edits made to the PR, issue #507, or any
`.github/workflows/**` file); `.github/workflows/peer-review-orchestrator.yml` — `on:` block
(`pull_request_target` + `issue_comment: [created]`), `relevantEvent` gate and `isCurrentProviderRequest`
helper, and the "Request supported provider reviews through OPERATOR" step that posts the
self-qualifying comment under the default operator login.
