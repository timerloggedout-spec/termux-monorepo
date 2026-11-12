# Tribute System 1 — fast routing for maintainer replies

System 1 sits in front of the Tribute (help-wanted) lane. It reads maintainer
replies on our PRs and issues in **other people's repos** and routes them with
rules, regexes and lexicons: no LLM calls, stdlib only, GET-only network access.
It never posts on third-party repos.

| Piece | Path |
|---|---|
| Classifier, features, router, preflight, Gmail fallback, read-only ingest | `scripts/ci/tribute_system1.py` |
| Eval harness (CI gate) | `scripts/ci/tribute_system1_eval.py` |
| Labeled fixtures (3 real seeds + synthetic classes) | `tests/fixtures/tribute_system1/` |
| Tests | `tests/test_tribute_system1.py` |
| Workflow (eval on change; scan every 3h; backfill on dispatch) | `.github/workflows/tribute-system1.yml` |

## Pipeline
1. **Ingest**: `discover()` finds foreign PRs we authored (open *and* closed) and
   foreign issues we commented on; `hydrate()` pulls the thread, PR files,
   reviews and the linked issue. `parse_github_email()` turns a GitHub
   notification email (Gmail label `GitHub/Priority/Direct`) into the same
   shape. Comments dedupe by id.
2. **Features**: author role (owner / maintainer / contributor / other / bot /
   self), state + close actor, assignees (subject + linked issue), claims and
   claims made before our marker, skill/language requirements, placeholder diff
   (stake path, tiny diff, docs-only, TODO), reviews.
3. **Classify**: `closed_already_assigned`, `claimed_by_other`,
   `needs_human_skill`, `low_effort_placeholder`, `changes_requested`,
   `approved`, `merged`, `question_to_us`, `hostile_spam_flag`, each with a
   confidence and evidence. Curly apostrophes are handled.
4. **Route** (`route()`): primary label → action

| primary | action | re-engage allowed |
|---|---|---|
| merged | record_win | no |
| closed_already_assigned | retire_lane | no |
| needs_human_skill | drop_candidate | no |
| claimed_by_other | yield_lane | no |
| low_effort_placeholder | retire_lane | no |
| hostile_spam_flag (maintainer) | retire_lane_cooldown | no |
| question_to_us | llm_review (rung 2) | no |
| changes_requested | revise_patch | yes |
| approved | await_merge | yes |

Every decision also emits a `lane_event` (shape of `scripts/ops/lane_event.py`),
prefilter rules for scout/claim/contribute, and a Delphi reweighting signal.

## Escalation ladder (no HITL)
The Owner is the project's only human, so escalation means **re-planning, not a person**.
- **rung 0 `programmatic`**: deterministic checks (state, merged, assignee, close
  event, review state, diff size, claim timeline) settle the thread.
- **rung 1 `system1`**: token/feature/semantic classifiers (lexicons, regex) with
  confidence ≥ `TRIBUTE_S1_CONFIDENT` (0.75).
- **rung 2 `system2_llm`**: only what System 1 can't settle (low confidence,
  unlabelled human reply, `question_to_us`). Pass the verdict back as
  `route(thread, system2={...})`.
- **rung 3 `replan`**: the LLM is unsure → the system makes a new plan itself:
  yield (someone else claimed/assigned), retire (closed), or park the lane, then
  tighten scout/claim prefilters, reweight via Delphi, and pick the next candidate.

Never `AWAITING_APPROVAL`, never a `hark:queue` entry for a human.
`hitl_control_plane` gets an audit-only record (`state: RECORDED`). The only
Owner stops are the standing ones: destructive actions, secrets/credentials,
spending money, and posting on third-party repos. A drafted public reply is
recorded as `owner_required: post_on_third_party_repo`, the lane is parked, and
the system moves to the next candidate. That counts as HITL cost.

## Candidate preflight (before any claim comment or PR)
`preflight_candidate(issue, comments)` excludes issues that are assigned to
someone else, claimed by a human first, closed, or need a human skill
(language, marketing copy, "not for automated lanes"). `preflight_pr(files)`
blocks stake/placeholder-only PRs.

## Integration points (owned by the Tribute lane code)
- `tribute_followup.decide_action`: call `tribute_system1.reengage_allowed(thread)`
  before any `reengage` / `stale_nudge` post.
- `tribute_followup` search: include closed PRs and foreign issue threads.
- `tribute_scout` / `tribute_claim`: call `preflight_candidate`.
- `tribute_contribute`: call `preflight_pr`; stop opening stake-only PRs.
- `tribute-llm-assist`: only take rung-1 threads.
- Delphi: needs a `tribute-outcome` event in `delphi-signal.yml`'s enum.

## Eval
`python scripts/ci/tribute_system1_eval.py` reports per-class precision/recall,
action accuracy and the ladder costs: HITL rate (drive to zero), LLM-call rate,
re-plan rate, programmatic rate, and false re-engagements. CI fails on any false
re-engagement, HITL rate above 0, LLM-call rate above 0.35, any misrouted real
seed, or macro P/R below 0.9. Grow the set by
adding hydrated real threads (with an `expected` block) to the fixtures folder;
backfill output on branch `tribute-s1/backfill` is the source for new labels.

## Lane wiring (gates in the Tribute writers)

| Writer | Gate | Effect |
|---|---|---|
| `scripts/ci/tribute_followup.py` | `hydrate` then `reengage_allowed(thread)` before every `reengage` / `stale_nudge` post | Post skipped unless System 1 allows it (fails closed on any read error). Closed foreign PRs from the last `HELP_WANTED_LESSON_DAYS` (default 14) are routed into a `followup_lesson` evidence row, once per PR, and are never posted on. |
| `scripts/ci/tribute_scout.py` | `preflight_candidate(issue, comments)` | Ineligible issues (assigned elsewhere, prior human claim, human skill/language, closed, comments unreadable) are moved to the catalog's `excluded` list. |
| `scripts/ci/tribute_claim.py` | `preflight_candidate` before the claim comment and fork | Ineligible = no comment, no fork, exit 0 with `claim_skipped_preflight`. |
| `scripts/ci/tribute_contribute.py` | real patch required (`--patch` / `HELP_WANTED_PATCH`), candidate preflight, then `preflight_pr(files)` on the staged diff | Stake-only PRs (`.github/help-wanted-lane-stake.md`) are retired; no fallback issue notice. |
| `.github/workflows/tribute-llm-assist.yml` | `route(hydrate(...))["rung"] == "system2_llm"` | Only rung-1 threads get an LLM pass; explicit inputs are gated too. |

Regression: `tests/test_tribute_system1_gates.py` proves the three seed fixtures never trigger a follow-up post, claim, or PR.

## v2 (schema `tribute-system1/v2`)

Learned from the 208-thread backfill (since 2026-09-01) and 20 real threads now in
`tests/fixtures/tribute_system1/real_backfill_cases.json`:

| Change | Why |
|---|---|
| Language rule needs a named language (`fluent Turkish speaker`) or `speakers` | v1 flagged "native build" / "fluent API" as `language:unspecified` (codex-termux#14, hermes-agent#8993). |
| Spam regex: `reported` alone is no longer spam; ban/repoban requests are confident (0.80) | v1 sent two maintainer threads to HITL on the word "reported" (Haven#273, pyrite#192). |
| New label `closed_resolved` -> `retire_lane` (weight -0.2) + prefilter `require_open_issue` | Issues closed by the maintainer (fixed, shipped) were claimed anyway, including after close. |
| Drips/Stellar Wave: `has applied to work on this issue`, `application was accepted`, `completed by @x` | Program-assigned issues are claimed by the program; `skip_bounty_program_issue`, and `preflight_candidate` refuses them. |
| Semantic layer (bag-of-stems cosine vs class prototypes; no model, no LLM) | Corroborates token hits and blocks re-engagement when the last external comment semantically declines. |
| Placeholder merge: `merged` + `low_effort_placeholder` -> `record_placeholder_merge`, Delphi weight **0** | All 14 stake-file merges are not contributions; they never count as a win. |
| Follow-up cap `TRIBUTE_S1_FOLLOWUP_CAP` (default 2) unanswered own comments | sendam#492 carried 6 unanswered stale nudges. |
| Issue threads never get a follow-up; only our own open PRs can | A re-engagement on someone else's issue is never ours to send. |

`reengage_block` names why a follow-up was refused (`class`, `followup_cap`,
`semantic_decline`, `closed`, `not_addressed_to_us`, `issue_thread`, `rung`).
Tests: `tests/test_tribute_system1_v2.py`.

## Delphi emission (tribute-outcome)

`tribute-system1.yml` route job -> `scripts/ci/tribute_s1_delphi_delta.py` ->
`delphi-emit` job (`uses: ./.github/workflows/delphi-signal.yml`, `event: tribute-outcome`).
Only **changed** outcomes go out, one per thread (`key` = thread URL); the last
emitted value per thread is kept in `state/delphi-emitted.json` on branch
`tribute-s1/backfill`, written only after the emit succeeds. At most 200 per run;
the rest emit next run. `delphi-tribute-ingest.yml` keeps its manual backfill
path; its `workflow_run` path is off unless `vars.TRIBUTE_INGEST_ON_RUN == 'true'`
(it failed on every PR eval run, which has no decisions artifact).

## LLM assist never posts

`tribute-llm-assist.yml` writes its plan to the `tribute-llm-assist-plan`
artifact, the step summary, and an evidence row `kind=llm_assist_plan, posted=false`.
It no longer comments on the foreign PR: a public comment on a foreign repo needs owner approval.
