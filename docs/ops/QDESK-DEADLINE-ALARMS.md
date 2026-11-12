# QDesk deadline desk: requirement closure and deadline alarms

Owner: the QUE desk (QDesk). Code: `scripts/que/qdesk_deadlines.py` and `scripts/que/pages_freshness.py`. Workflow: `.github/workflows/qdesk-deadline-desk.yml`. Page: `apps/tribute-dashboard/qdesk-gantt.html` (nav "QDesk Gantt").

## Why this exists (2026-11-11 post-mortem)

The Amazon Research Awards cycle (coordinator entry **C15**) closed at Wed 2026-11-11 11:59 PM PST without an entry. On 11-03 Amazon confirmed that Model A, a PI employed by a 501(c)(3) fiscal sponsor, satisfies Rules §I. The 11-10 re-screen (#5138, commit 3eab485) still kept FAIL because no sponsor or PI was in place. Root causes:

1. **Candidates were invisible to the countdowns.** `scripts/challenge_entries/countdowns.py` and the coordinator's `derived.countdowns` covered `events` (D0–D5) only. C11–C16 live in `candidate_events`, which no countdown, alarm or Gantt read. `derived.computed_at` was last written Wed 2026-10-28 12:53 PM PDT.
2. **Requirements were prose, not tasks.** The unmet clause sat in `status` and `institution_gap` text. Nothing converted it into a dated, owned closure task, so "fiscal sponsor" had no start date, no due date and no owner.
3. **No escalation path.** The countdown refresh ran weekly (Mondays) and wrote a Markdown block. Nothing opened a `hark:queue` job as a deadline approached, so a slip was silent by design.
4. **Classification froze the entry.** `SCREENED OUT` / `FAIL` / `HOLD` were treated as terminal. They are gaps with a closure route: for C15, a fiscal sponsor that can employ the PI.

## What runs now

Every 2 hours, and on any change to the coordinator:

- **Plan.** Every entry in `events` and `candidate_events` gets a governing deadline. The earliest of `deadline`, `*_due`, `submission*` and `*close*` governs; `*_open`, decision and cohort dates are ignored. Each entry is then classified as `done`, `gap` or `open`.
- **Requirement-closure tasks** are written to `ops/challenge/qdesk-plan.json` and to the Gantt filing format at `ops/challenge/qdesk-requirements.gantt.txt`, which compiles with `scripts/temporal/gantt_compile.py`.
  - An institution gap (PI, fiscal sponsor, NGO, legal ability to receive funds) gets this chain: sponsor shortlist → PI route → sponsor application (draft) → **owner signs** (the only HITL step) → re-screen and register → draft and submit. It is dated against the live deadline when one is more than 3 days out, otherwise against the next cycle.
  - Every open gate becomes a closure task. A pending go/no-go becomes a decision task.
  - Task state and first-planned dates persist across runs.
- **Alarms** (escalated inside GitHub Actions: `qdesk:alarm` issue → `qdesk:P0` + owner assignment at 48h → red run + `::error` at 12h/MISSED, plus `repository_dispatch qdesk-alarm` for any internal lane; the hark:queue copy is only a mirror) fire at **T-7d (P1), T-48h (P0), T-12h (P0) and MISSED (P0)** for every entry that is not done. Each tier fires once per entry and deadline (`alarms_sent` in the plan). The 2-hour cadence means a T-12h alarm always lands with at least 10 hours to act. Alarms go through `hark-enqueue.yml` as `hark:queue` issues, keyed `qdesk-deadline:<entry>:<date>` (project `main`).
- **HITL rate** = owner steps ÷ tasks, shown on the page and in the run summary. Only money, legal attestations, binding agreements and credentials are tagged `hitl`, and each one carries a ready-to-approve `owner_packet`. Everything else is agent work.

## Page freshness

`ops/challenge/qdesk-pages.json` lists the tracking pages. Each run checks:

- **Served SHA vs master** for gh-pages, the user-site Tribute / help-wanted pages and Vercel production.
- **Stamp age** for the generated feeds.

A stale or broken page opens a `hark:queue` job (project `deploy-quota`), one per page per day. The `vercel-census` job prints a names-only count of the last 24h of Vercel deployments, which shows what consumes the Hobby cap of 100 per day.

### Audit at build time (Thu 2026-11-12 ~00:00 PST, master d0f01e9)

| Page | Served | Verdict |
|---|---|---|
| https://timerloggedout-spec.github.io/termux-monorepo/ (gh-pages) | f00585e, 2h old | ok |
| https://timerloggedout-spec.github.io/help-wanted/ | f00585e (`control_surface.source_sha`) | ok |
| https://timerloggedout-spec.github.io/tribute/ | f00585e | ok |
| https://tribute-oversight.vercel.app | 083a9b2, from run 41399064480 on Sun 2026-11-01 | **stale, 10 days** |
| https://tribute-dash.vercel.app | 083a9b2 | **stale, 10 days** |
| https://help-wanted-oversight.vercel.app | `DEPLOYMENT_NOT_FOUND` (404) | **retired alias**. The project was renamed tribute-oversight; repoint links |
| marketing-gantt feed (`/tribute/data/marketing-gantt.json`) | generated Mon 2026-11-09 9:12 AM PST | ok (weekly feed) |

**Vercel root cause:** the `tribute-vercel-prod` runs on Nov 3, 6, 8, 10 and 11 (42262638671, 42505400560, 42865853464, 43069016012) all failed at `promote-master-to-vercel-production` with `Resource is limited - try again in 24 hours (more than 100, code: "api-deployments-free-per-day")`. The daily 09:31 PT promote runs after other deploys have spent the account's 100/day Hobby quota. The census job names those deploys. The fix is quota allocation (deploy-quota lane), not code.

## Collector failures fixed here

- `delphi-rfp-feed-collect`: failed red when the shared installation bucket was empty, for example run 43163689995: `rfp fetch failed status=403 ... API rate limit exceeded for installation`. It now defers cleanly (`deferred=true`, warning annotation, feed unchanged) instead of failing.
- `delphi-tribute-ingest`: failed every run from 2026-11-02 (for example 41748985992) because it fired on tribute-system1 pull_request/push runs, which publish no `tribute-s1-decisions` artifact. It now ingests only after schedule/dispatch scans and treats a missing artifact as "nothing to ingest".
- `proposals-feed-collect`: green on master since 2026-11-10. `proposal-lifecycle` failures are pull_request validations of others' PRs (`validate_registry.py`) and are not master breakage.

## Discovery and registration cadence

The following already run on schedules: `opportunity-cycle.yml` (daily 13:17 UTC), `challenge-osint-watch.yml` (weekly) and `registration-monikers.yml` (weekly). New entries they add to the coordinator re-trigger this desk on push, so a newly discovered event gets tasks and alarms within minutes. Registrations use the LoggedOut Timer / timerloggedout / timerloggedout@gmail.com monikers, passwordless where possible.
