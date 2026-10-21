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
| hostile_spam_flag (maintainer) | escalate (hitl) + repo cooldown | no |
| question_to_us | escalate (hitl) | no |
| changes_requested | revise_patch | yes |
| approved | await_merge | yes |

Every decision also emits a `lane_event` (shape of `scripts/ops/lane_event.py`),
prefilter rules for scout/claim/contribute, and a Delphi reweighting signal.

## Escalation ladder
- **rung 0 `system1`**: a label ≥ `TRIBUTE_S1_CONFIDENT` (0.75) → auto-route.
- **rung 1 `system2_llm`**: low confidence or an unlabelled human reply →
  LLM pass (help-wanted-llm-assist). Pass its verdict back as
  `route(thread, system2={...})`; a confident verdict returns to rung 0.
- **rung 2 `hitl`**: LLM unsure, `question_to_us`, or a maintainer spam flag →
  `hitl_control_plane` proposal in `AWAITING_APPROVAL` → `hark:queue` issue via
  `hark-enqueue.yml` (enabled with repo variable `TRIBUTE_S1_ENQUEUE=true`).
  Nothing is posted upstream without the user's OK.

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
action accuracy, escalation rate and false re-engagements. CI fails on any false
re-engagement, any misrouted real seed, or macro P/R below 0.9. Grow the set by
adding hydrated real threads (with an `expected` block) to the fixtures folder;
backfill output on branch `tribute-s1/backfill` is the source for new labels.

## Lane wiring (gates in the Tribute writers)

| Writer | Gate | Effect |
|---|---|---|
| `scripts/ci/help_wanted_followup.py` | `hydrate` then `reengage_allowed(thread)` before every `reengage` / `stale_nudge` post | Post skipped unless System 1 allows it (fails closed on any read error). Closed foreign PRs from the last `HELP_WANTED_LESSON_DAYS` (default 14) are routed into a `followup_lesson` evidence row, once per PR, and are never posted on. |
| `scripts/ci/help_wanted_scout.py` | `preflight_candidate(issue, comments)` | Ineligible issues (assigned elsewhere, prior human claim, human skill/language, closed, comments unreadable) are moved to the catalog's `excluded` list. |
| `scripts/ci/help_wanted_claim.py` | `preflight_candidate` before the claim comment and fork | Ineligible = no comment, no fork, exit 0 with `claim_skipped_preflight`. |
| `scripts/ci/help_wanted_contribute.py` | real patch required (`--patch` / `HELP_WANTED_PATCH`), candidate preflight, then `preflight_pr(files)` on the staged diff | Stake-only PRs (`.github/help-wanted-lane-stake.md`) are retired; no fallback issue notice. |
| `.github/workflows/help-wanted-llm-assist.yml` | `route(hydrate(...))["rung"] == "system2_llm"` | Only rung-1 threads get an LLM pass; explicit inputs are gated too. |

Regression: `tests/test_tribute_system1_gates.py` proves the three seed fixtures never trigger a follow-up post, claim, or PR.
