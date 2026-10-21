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
- `help_wanted_followup.decide_action`: call `tribute_system1.reengage_allowed(thread)`
  before any `reengage` / `stale_nudge` post.
- `help_wanted_followup` search: include closed PRs and foreign issue threads.
- `help_wanted_scout` / `help_wanted_claim`: call `preflight_candidate`.
- `help_wanted_contribute`: call `preflight_pr`; stop opening stake-only PRs.
- `help-wanted-llm-assist`: only take rung-1 threads.
- Delphi: needs a `tribute-outcome` event in `delphi-signal.yml`'s enum.

## Eval
`python scripts/ci/tribute_system1_eval.py` reports per-class precision/recall,
action accuracy and the ladder costs: HITL rate (drive to zero), LLM-call rate,
re-plan rate, programmatic rate, and false re-engagements. CI fails on any false
re-engagement, HITL rate above 0, LLM-call rate above 0.35, any misrouted real
seed, or macro P/R below 0.9. Grow the set by
adding hydrated real threads (with an `expected` block) to the fixtures folder;
backfill output on branch `tribute-s1/backfill` is the source for new labels.
