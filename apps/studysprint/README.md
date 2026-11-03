# StudySprint — D1 (Workshop to Ship)

Frozen pick for packet D1, 2026-10-30 (Manager-enacted freeze, owner
mandate). Concept detail: the Delphi lane's brief-first generation record
on the official brief evidence pack
(`docs/ops/CHALLENGE-BRIEF-EVIDENCE-2026-10-28.md`, D1 section).

## What it is

A Strands-wired agent for first-gen college students: a verified
syllabus -> a week-by-week study plan, recall quizzes, and re-plans
on missed weeks. It extends the D0 mandate-practice agent (Delphi
Oracle evidence gate + `fetch_evidence`, vendored in `foundation/`)
with one new tool, `fetch_study_evidence` (syllabus + practice_set
kinds, same stamped-evidence shape).

## Files

| File | Role |
|---|---|
| `agent.py` | The agent: D0 gate loop + StudySprint tools + Strands registration |
| `study_tools.py` | G2 study evidence kinds + plan/quiz/replan tools |
| `foundation/` | D0 foundation, verbatim: oracle kernel (blob 9a4a1c78), fetch_evidence (8442d813), census |
| `demo.py` / `demo-script.md` | <3-min demo; writes `evidence/demo-run.json` |
| `article.md` | Builder Center article draft (submission item 2) |
| `examples/` | Sample syllabus + practice set (synthetic) |
| `tests/test_studysprint.py` | Offline gate tests |
| `tools/resync_parity.py` | Nov 3 re-sync parity auditor (blob parity vs `timerloggedout-spec/studysprint`) |
| `tests/test_resync_parity.py` | Parity audit + Now features tests |

## Live assets

- Article (Builder Center): https://builder.aws.com/content/3LRJhGucOZfz9ydzFax8sD2p5yB/studysprint-a-study-plan-you-can-trust-built-with-the-strands-agents-sdk
**Update — Oct 31, 2026: StudySprint v0.2.0 is out.** Five new
features, all from the Now list: a trust receipt BEFORE the plan —
see exactly what your syllabus proved before a single study block
exists · a Today view with a guilt-free 'I missed this' · time-budget
reflow (25 or 45 minutes — the plan reshapes around your day) ·
daily check-in with recovered-weeks streaks · plain-language mode,
receipts minus the jargon. Release:
https://github.com/timerloggedout-spec/studysprint/releases/tag/v0.2.0
— new v0.2.0 demo:
**Update — Nov 2, 2026: StudySprint v0.3.0 is out.** Spaced
repetition, built on the plan: FSRS + SM-2 schedulers, Anki .apkg
export, an Obsidian vault surface, and a ts-fsrs seed for the UX
layer. Release:
https://github.com/timerloggedout-spec/studysprint/releases/tag/v0.3.0
— new v0.3.0 demo:
**Update — Nov 3, 2026: StudySprint v0.4.0 is out.** The reading
pipeline (finder → term bank), multi-course planning with exam
countdowns and .ics export, and memory methods — Temple Memory,
Pomodoro pacing, and reminders that carry the memory cue. Release:
https://github.com/timerloggedout-spec/studysprint/releases/tag/v0.4.0
— new v0.4.0 demo:
- Demo video (YouTube, 2:54, public): https://www.youtube.com/watch?v=WK9LMwpvHUk
- Starting-agent (D0) repo: https://github.com/timerloggedout-spec/delphi-oracle

## Impact

One syllabus becomes a 12-session study plan. A daily check-in
takes about 30 seconds. A missed session is re-planned in one tap
— never punished.

Plain-language mode explains every plan in simple words first —
built for students studying in a second language.

Most study tools plan from raw text and invent the rest.
StudySprint plans only from verified evidence: when a claim about
your course can't be verified, the agent abstains instead of
guessing — and every plan carries a receipt showing what it was
built from. The planning kernel extends the Delphi Oracle from
the fleet's earlier challenge: evidence-gating that has already
shipped once.

## Product + process

- `FEATURES.md` — features a user would want, UI/UX principles, roadmap
- `VERSIONING.md` + `VERSION` + `CHANGELOG.md` — SemVer process;
  1.0.0 = the Nov 4 submission release

## Run it

```bash
python3 demo.py
python3 -m pytest tests/
```

### Nov 3 Re-sync Parity Test

To verify blob parity between this monorepo's `apps/studysprint` tree and the upstream `timerloggedout-spec/studysprint` repo (or a local checkout):

```bash
# Against upstream GitHub API:
python3 tools/resync_parity.py

# Against a local checkout pair:
python3 tools/resync_parity.py --target-dir /path/to/studysprint-checkout

# Offline verification (against frozen baseline manifest):
python3 tools/resync_parity.py --offline

# Machine-readable JSON output:
python3 tools/resync_parity.py --json
```
The re-sync parity script exits `0` on verified parity and `1` (non-zero) on detected drift.

Receipts (sample syllabus): asserted-only -> ABSTAIN; fetched
syllabus -> ALLOW_RECOMMENDATION + 12-session plan + quiz + re-plan;
credential_mutation -> ESCALATE. No live deployment of StudySprint is
claimed; receipts state `deployment: False` and whether the Strands
SDK was importable in the run environment.

Reading ships too: the multi-pass RSVP reader (`study_reader.py`,
in v0.3.0) reads section by section — a fast skim pass, then a
focused re-read — with one-tap term flagging into the SR deck.
