# Challenge Recruitment — pipeline of record

Seat: recruitment (reports to `challenge-entries-manager`). Mission:
find potential recruits from challenge participants/judges, build the
database, find their GitHubs, execute MoneyBall v2 metrics. Autonomous;
no approval gates. Engagement autonomous under the event entrant
moniker, every touchpoint logged `{surface, at, content_ref}`.

## Flow
- SOURCE: `ops/challenge/coordinator.json` participants/judges (entries lane a33d3ca1).
- SCORE: MoneyBall plane v2 pattern (axes fixed at event intake in coordinator `moneyball{}`, composite recomputed, flag = composite >= threshold AND no unverified axis AND v2-valid).
- STORE: Neon `recruitment_current` view (DB lane e3055a9c schema) is the working DB; provisioning of LANE_EVENTS_DATABASE_URL/NEON_API_KEY pending — rows queue in `ops/challenge-recruitment/registry.json` until then.
- ASSIST: manager's assistant (a440bcb2) owns opportunity-cost + OSINT wiring — coordinate, don't duplicate.

## Pipeline
States: `identified -> profiled -> engaged -> in_talks -> collaborator | passed`.
Registry: `ops/challenge-recruitment/registry.json` (challenge-recruitment/v1).
GitHub profiles: `ops/challenge-recruitment/github-profiles/<event>--<entity>.json` — public API snapshots, sourced + fetched_at, append-only snapshots in coordinator `signals.snapshots[]`.
GitHub hunt: project repo/demo links, public profiles, commit authorship only; confidence recorded; unmatched = NOT_ESTABLISHED; no guessed handles; no personal identifiers beyond public professional profiles (commit emails never recorded).

## Population at stand-up (2026-10-28)
Entities tracked 1 (D1 participant), judges 0, GitHub matched 1/1 (100%).
D4 gallery Oct 30 = first big field; D2 Nov 5; D5 Nov 17; D3 post-Nov 13.
