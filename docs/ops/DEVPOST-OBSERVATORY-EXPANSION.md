# Devpost Observatory Expansion

Status: architecture proposal; source reconnaissance completed 2026-11-22.
Owner: challenge-entries lane (event records) + Devpost directory adapter (global project discovery).
Authority: public-source observation only. Existing lane ownership and single-writer boundaries remain in force.

## Observatory-wide concept intelligence

The Devpost adapters are one Observatory source family. The source-neutral concept corpus and challenge-outcome comparison/prediction design are specified in [`docs/superpowers/specs/2026-11-22-observatory-concept-intelligence-design.md`](../superpowers/specs/2026-11-22-observatory-concept-intelligence-design.md). That design separates independent concept value from official award outcomes and defines leakage-safe evidence gates before predictive probabilities.

## 1. Decision

Extend the existing Challenge OSINT and Observatory system with two distinct Devpost source adapters:

1. **Devpost event adapter** — event pages, rules, schedules, prizes, criteria, announcements, galleries, participants, judges, and results.
2. **Devpost software-directory adapter** — global project discovery across Staff Picks, Popular, Trending, hackathon collections, search/filter results, and supported advanced-search queries.

Keep these adapters separate. The authenticated Devpost connector supplies event and account-scoped capabilities; global software-directory discovery belongs to a dedicated public-page observation adapter.

The existing challenge coordinator remains the canonical event record. The directory adapter owns its candidate/observation index. Cross-plane graph imports both read-only and derives links while preserving each source plane's ownership.

## 2. Existing capability inventory

The repository already provides the bulk of the lifecycle model:

- `ops/challenge/coordinator.json` is the machine-readable source of truth for events, projects, participants, judges, organizers, prizes, and outcomes.
- `docs/ops/CHALLENGE-SCHEMA.md` defines public participant profiles, project links, judging history, public criteria, statements, append-only signals, and placements.
- `docs/ops/CHALLENGE-OSINT.md` defines event/project/competitor/judge/prize observation and the weekly official-page hash watcher.
- `scripts/challenge/osint_watch.py` and `.github/workflows/challenge-osint-watch.yml` maintain append-only official-page snapshots and refresh PRs.
- `scripts/challenge/participant_event.py` mirrors participant, judge, signal, and OSINT snapshot data into the existing Neon store.
- `scripts/graph/cross_plane_link.py` imports the challenge plane read-only into the cross-plane graph.
- `docs/ops/CHALLENGE-ENTRIES-LOG.md` records registrations separately from submissions and requires evidence for each claim.

This proposal adds source coverage and discovery on top of those capabilities.

## 3. Source boundary

### 3.1 Devpost event connector

Use the Devpost Hackathons connector for its supported event/account operations:

- open/upcoming event discovery and keyword event search;
- event overview and status;
- key dates and current phase;
- rules and eligibility;
- submission requirements;
- prizes;
- judging criteria and tracks;
- announcements;
- authenticated user's connected events, projects, and editable project details.

Use these responses as structured event evidence. Record the connector fetch timestamp and completeness status with every observation.

Connector boundary: these actions cover event/account data. Global Devpost software-directory search belongs to the public-page adapter.

### 3.2 Public software-directory adapter

Observe the public directory at `https://devpost.com/software/` and its public listing surfaces:

- Staff Picks;
- Popular;
- Trending;
- event-specific project collections/galleries;
- public search and filters;
- documented advanced search operators;
- visible technology tags and category facets.

The adapter discovers candidates and records listing context. Official competition placement comes from organizer result sources; directory position, likes, comments, and popularity labels remain independent signals.

Collection method order:

1. documented/public machine-readable surface, where available;
2. public HTML page observation using a bounded, terms-compliant fetch;
3. browser observation for dynamic pages that require normal page interaction.

Respect site terms, robots directives, rate limits, and access boundaries. Use public signed-out content. Record blocked, unavailable, or incomplete surfaces explicitly; route access-restricted pages through an authorized source path.

### 3.3 Other public evidence

For competitor projects, participants, judges, and winners, use the public event gallery, public project pages, official organizer announcements, official winner posts, and voluntarily published public profiles. Follow explicit public links for GitHub repositories, demos, portfolios, and articles. Keep each field tied to its source URL and fetch time.

## 4. Lifecycle model: BEFORE / DURING / AFTER

Every tracked event has a lifecycle phase and phase-specific observation coverage.

### BEFORE — event intelligence and baseline

Capture:

- event identity, host, sponsors, platform, venue/location, format, and public organizers;
- announcement, registration, build, submission, judging, voting, and winner dates with timezone;
- official rules, eligibility, tracks, deliverables, required technologies, and judging criteria;
- prize tiers and source URLs;
- publicly named judges, affiliations, published criteria, and prior public judging history;
- participant/competitor baseline when a public participant surface exists;
- prior comparable events, public winners, projects, placements, and recurring patterns;
- the user's own registered events and project state through account-scoped connector reads.

Create a baseline snapshot before the event becomes active wherever the public surface allows it. Store field-size counters separately from the number of individually tracked public records.

### DURING — event and competitor watch

Observe:

- official announcements, rule changes, schedule shifts, prize changes, and new organizer/judge disclosures;
- gallery opening, new submissions, project metadata, public repositories, demos, articles, and technology tags;
- participant/team public profiles and explicitly published links;
- project engagement metrics as time-series observations;
- our own project publication/submission state and public artifact changes;
- event phase transitions and deadline proximity.

Keep event-page snapshots append-only and record deltas with old/new hashes and source timestamps. A failed or blocked fetch creates an observation-gap record; page/event change state remains unknown until a successful observation.

### AFTER — results, podium, judges, and learning

Capture:

- official winners announcement and result source;
- event-specific placement/rank, prize tier, category/track, project, team, and public member identities;
- honorable mentions, finalist lists, and other explicitly published distinctions;
- judge panel as actually published at results time, with name, role, organization, profile/source links, and confidence;
- judging criteria and any publicly disclosed weighting or score details;
- winner project writeups, repositories, demos, architecture patterns, technical choices, and open-source contributions;
- corrections, disqualifications, eligibility verification, and delayed result announcements as new observations.

Preserve the distinction between:
- **official event placement** — a result published by the organizer/platform;
- **directory placement** — Staff Pick, Popular, Trending, or search position;
- **engagement** — likes, comments, views, or other displayed counters;
- **our analytical ranking** — an internal, versioned comparison with explicit methodology.

Keep directory ranking, official event results, judge coverage, and published scores as separate fields. Represent unnamed judges as partial coverage and record scores from disclosed source material.

## 5. Data and identity contract

Keep the current canonical event structures in `ops/challenge/coordinator.json`. Add directory observations in a separately owned source tree, proposed:

```text
ops/challenge/devpost-directory/
  manifest.json
  candidates.jsonl
  snapshots.jsonl
  coverage.json
```

Suggested record shape:

```json
{
  "schema_version": "devpost-directory-observation/v1",
  "project_id": "devpost:project:<stable-slug>",
  "project_url": "https://devpost.com/software/<slug>",
  "title": "Published project title",
  "tagline": null,
  "listing_surface": "staff_picks",
  "listing_position": 1,
  "event_url": null,
  "technology_tags": [],
  "displayed_metrics": {},
  "observed_at": "2026-11-22T00:00:00Z",
  "fetched_at": "2026-11-22T00:00:00Z",
  "source_url": "https://devpost.com/software/",
  "source_sha256": "<sha256>",
  "field_confidence": "medium"
}
```

The example illustrates schema shape. Preserve missing fields as null/empty with explicit coverage; require direct evidence for team identity, event placement, judge identity, and technology use.

Stable identity rules:

- Prefer canonical Devpost project URL/slug.
- Preserve the event's canonical Devpost URL/subdomain and numeric ID when the connector supplies them.
- Resolve a project's GitHub repository only from an explicit public repository URL on the project page or linked public project material.
- Link participants to projects using explicit published project/team references.
- Keep event-scoped challenge project identities separate from global directory project identities; join them by canonical URL when verified.
- Preserve first_seen, last_seen, and append-only observation history. Deduplicate by canonical identity + source snapshot hash.

## 6. Graph integration

The cross-plane graph remains a derived, regenerable view. Extend its challenge import only after the directory schema and tests are stable.

Proposed graph entities:

- `devpost:project:{slug}` — global software-directory project;
- existing `challenge:event:{id}` — event;
- existing `challenge:participant:{event}/{key}` — public participant/team;
- existing `challenge:judge:{slug}` — publicly named judge;
- existing `challenge:organizer:{slug}` — organizer.

Proposed evidence-backed links:

- directory project `--listed_on-->` Devpost surface;
- directory project `--submitted_to-->` event;
- participant `--entered_with-->` project;
- project `--hosted_at-->` GitHub repository;
- judge `--judges-->` event;
- project/participant `--placed_in-->` event result (new typed edge, only after schema review).

The graph importer reads directory and event records and preserves both source planes as read-only. Add edge types and plane enums through the graph schema, validator, deterministic builder, and regression tests in one coherent change. Apply privacy rules: public links, explicit identity evidence, identity joins grounded in verified identifiers, and internal MoneyBall metrics excluded from public graph projections.

## 7. Observation cadence

The following cadence is proposed; workflow configuration requires a separate implementation and observed run.

| Frequency / trigger | Observation | Purpose |
|---|---|---|
| Weekly | Devpost software directory: Staff Picks, Popular, Trending, selected filters/searches | Discover reference candidates and emerging patterns |
| Weekly | Open/upcoming Devpost hackathons | Identify relevant challenges and event opportunities |
| Daily while active | Tracked event announcements, deadlines, dates, status, and official page hashes | Catch material schedule/rule changes |
| Event phase transition | Gallery opening, judging start/end, winner announcement | Trigger phase-specific collection |
| During active build/submission windows | Public gallery/project deltas at a bounded event-aware interval | Observe competitor/project movement |
| After results | Winner/project/judge capture and result verification | Build podium and longitudinal evidence |
| Monthly | Reference-template reassessment | Retire, promote, or expand candidates |

Keep the existing weekly challenge OSINT watcher as the event-page baseline. Add directory discovery as a sibling workflow with its own concurrency group, source state, and refresh PR. Keep the discovery sweep bounded and idempotent. Daily checks apply to tracked active events; full-catalog crawling follows a separate bounded discovery cadence.

## 8. Reference-template and MoneyBall output

Promoted reference projects should carry:

- event and track;
- official placement, if published;
- judge panel coverage and source confidence;
- project/repository/demo links;
- problem and user;
- technical architecture and integrations;
- agent/tool execution pattern;
- evaluation/evidence approach;
- real-world usefulness signal;
- reusable implementation pattern;
- limitations and failure modes;
- observed open-source contribution;
- source snapshot IDs and fetch timestamps.

Keep raw observations separate from interpretation. Candidate promotion/retirement is a versioned decision with evidence. Treat directory popularity as a discovery feature; evaluate engineering quality and competition outcomes through separate evidence.

## 9. DataHub reference case — connector-verified 2026-11-22

The Devpost connector was exercised against **Build with DataHub: The Agent Hackathon** (event ID 28039; `https://datahub.devpost.com/`).

Observed connector evidence:

- Event status: `closed`, raw status `winners_announced`.
- Submissions: 2026-07-06 13:00Z through 2026-08-10 21:00Z.
- Judging: 2026-08-17 14:00Z through 2026-08-31 21:00Z.
- Winners announced: 2026-09-10 18:00Z.
- Prize pool: $20,500; Grand Prize $6,000 (1), Challenge Winners $3,000 (4), Honourable Mention $1,000 (2), Most Valuable Feedback $50 (10).
- Six judging criteria: Use of DataHub, Technical Execution, Originality, Real-World Usefulness, Submission Quality, and a bonus for meaningful open-source contribution.
- The event page exposed eight judge names and affiliations through its public judges section.
- The connector returned eight announcements, including the winner announcement and a September 4 schedule update moving the announcement to September 10.

The public rules describe a two-stage process: baseline viability followed by equally weighted substantive criteria. The rules allow judge rosters to change and may omit individual names. Preserve the distinction between the public page's named judge list and the complete adjudication panel, which can remain unknown.

The public event page listed these eight judges/affiliations at fetch time: Aman Gairola (Engineering Manager, Pinterest); Maggie Hays (Founding Product Manager, DataHub); Alyssa Lee (Chief of Staff, DataHub); Adrian Machado (Software Engineer, DataHub); Tim Bossenmaier (Data Architect, Cloudflight); Mike Burke (Senior Developer); Nick Adams (DataHub); and Wenjia You (Member of Technical Program Staff, OpenAI). Store these as the **publicly listed panel snapshot**, with the page URL and fetched_at. Preserve the event-rules caveat that the complete/final panel may differ or include unnamed judges.

The organizer's winner article reports 600+ submissions and seven prize-winning projects. Its published result order/categories are:

| Official result | Track / distinction | Project | Publicly named builder(s) |
|---|---|---|---|
| Grand Prize | Overall | Project Blackbox | Alex Velazquez |
| Challenge Winner | Agents that do real work | Hindsight | Germán Massello |
| Challenge Winner | Metadata-aware code generation | Schema-Drift Auto-Repair Agent | Yadnesh Salvi |
| Challenge Winner | Production ML | Culprit | Jonathan Andrei |
| Challenge Winner | Open and wildcard | Paracelsus | Lutfiya Miller; Chris Müller |
| Honourable Mention | — | ContextSeal | Mehmet Aydoğan |
| Honourable Mention | — | RippleProof | Muhammad Hassaan Javed |

This is an official-result taxonomy with award tiers and tracks. The article distinguishes Grand Prize, track challenge winners, and honorable mentions; numeric 1–7 rank: NOT_ESTABLISHED. Store the published award tier and track as separate fields; numeric podium rank remains null until the organizer explicitly publishes one.

The article describes evidence-gated agent execution, lineage-based root-cause analysis, human review, write-back verification, safe migrations, and writing incident resolution back to the catalog. It also reports 100+ open-source pull requests across DataHub repositories, skills, connectors, and documentation. Treat these as reference-pattern observations; apply them to individual winners when evidence supports the link.

Sources:
- Event: https://datahub.devpost.com/
- Rules: https://datahub.devpost.com/rules
- Updates: https://datahub.devpost.com/updates
- Schedule: https://datahub.devpost.com/details/dates
- Winner report: https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/

## 10. Current account-side Devpost observations — connector-verified 2026-11-22

The authenticated Devpost connector returned one published project:

- **Receipts Vault** — published at `https://devpost.com/software/receipts-vault`.
- Submitted to **UGREEN Hackathon 2026 on AI NAS** on 2026-11-16.
- Project details identify the repository folder `entries/c12-receipts-vault`, the proposal PDF, skill package ZIP, and package manifest.
- UGREEN event connector status is `judging` / `pre_winners_announced`.

The connector also returned three connected events: UGREEN (registered + submitted; judging), Cloud9 x JetBrains (registered; submissions open), and Learn AR with SPECS (registered; submissions open). These facts are account-scoped; global Devpost directory coverage remains separate.

For UGREEN, the connector reports submissions closed at 2026-11-16T07:45:00Z, judging from 2026-11-16T08:00:00Z through 2026-12-06T01:00:00Z, and winners announced at 2026-12-06T10:00:00Z (Pacific Time / connector UTC instants). Current phase: `judging`, fetched 2026-11-22T08:09:43Z. This gives the lifecycle watcher a live account-linked event with a published project and a future result transition.

Use these observations as a validation cohort for the BEFORE/DURING/AFTER state model. Refresh event dates and announcements before deadline-sensitive actions; preserve the connector's current status and fetch timestamp.

## 11. Implementation sequence and acceptance gates

1. **Adapter contract** — define directory schema, source identity, coverage states, and canonical URL normalization.
2. **Fixture corpus** — save sanitized public-page fixtures for Staff Picks, Popular, Trending, event gallery, project detail, and a winner announcement.
3. **Parser + tests** — deterministic extraction, pagination bounds, deduplication, malformed-page behavior, and explicit missing-field semantics.
4. **Directory collector** — bounded weekly discovery, append-only snapshots, source hashes, and refresh PR.
5. **Event lifecycle enrichment** — connect Devpost connector observations to existing coordinator event records; populate BEFORE/DURING/AFTER coverage.
6. **Podium capture** — capture official result placements and public judge records with source-level confidence.
7. **Graph extension** — add Devpost entities/edges through schema + builder + tests.
8. **SHE/MoneyBall projections** — compare reference patterns and longitudinal outcomes using raw evidence; evaluate directory position separately from quality.

Acceptance gates:

- Existing challenge coordinator remains the single writer for canonical event records.
- Directory collection remains separately owned and read-only to event records.
- Every populated fact has a source URL, fetched_at, and confidence/coverage state.
- Append-only snapshots preserve history and source hashes.
- Directory ranking, official placement, engagement, and internal analytical ranking remain distinct.
- Judge identities and scores remain source-grounded; hidden judges/scores remain unknown.
- Public graph views exclude internal metrics and identity joins based on names alone.
- Collector tests cover terms/access boundaries, pagination, deduplication, and partial-source failures.
- Cadence is reported as configured only after a workflow exists and a real scheduled run is observed.

## 12. Explicit non-goals

- Treating Devpost's authenticated event connector as a global project-directory API.
- Scraping login-gated participant lists or bypassing anti-bot controls.
- Treating Staff Picks, Popular, Trending, likes, or comments as official event rankings.
- Inferring judge identities or undisclosed scoring.
- Replacing the existing Challenge OSINT watcher, coordinator, Neon mirror, or cross-plane graph.
- Claiming a proposed cadence is active before its workflow is deployed and observed.


## 13. GitLab AI Hackathon source family — connector + public hierarchy reference

The Challenge OSINT lane now has a GitLab source-family dossier:
[`GITLAB-AI-HACKATHON-OSINT.md`](GITLAB-AI-HACKATHON-OSINT.md), backed by
`ops/challenge/osint/gitlab-sources.json`. This is a cross-venue source set, separate from the Devpost global
software-directory adapter.

The public GitLab hierarchy was observed 2026-11-22. The sibling `transcend` subgroup API returned **312 public projects**; its
exact event-cycle mapping remains `NOT_ESTABLISHED`. The explicitly archived
`transcend-october-2026` subgroup returned **1,273 child subgroups and 1,820
public archived projects**. Dated, privacy-minimized indexes are stored at
`ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`,
`ops/challenge/osint/gitlab-transcend-october-2026-subgroups-2026-11-22.ndjson`,
and `ops/challenge/osint/gitlab-transcend-october-2026-projects-2026-11-22.ndjson`:

- `gitlab-ai-hackathon` — public root group.
- `gitlab-devsecops-flow-hackathon` — child subgroup; its page showed zero
  child projects and zero child subgroups at fetch time.
- `transcend` — distinct child subgroup; public listing showed 312 items.
- `project-templates` — child subgroup containing the public
  `participant-template` project (project ID 77423853), with `agents/`,
  `flows/`, `LICENSE`, and `README.md`.
- `gitlab-profile` — public README points to the Devpost event.
- `participants-test-lee` (2 projects), `participants-test-mattias` (24
  projects), `test` (1 project), and `transcend-october-2026` (archived; 1,273
  participant subgroups / 1,820 public archived projects).
- Direct support projects: `ci` (participant CI configuration) and
  `security-policies` (pipeline policy project).

Connector-verified event references:

| Program | Submission window | Prize pool | Observed phase |
|---|---|---:|---|
| GitLab AI Hackathon (Feb–Mar 2026) | Feb 9 – Mar 25, 2026 | $65,000 | closed |
| Life After Code / GitLab Transcend (Oct 2026) | Oct 5 – Oct 27, 2026 | $45,000 | closed |
| GitLab Community Hackathon (Oct 2026; next Jan 2027) | Oct 6–12, 2026 historical; **Jan 21–28, 2027 upcoming** | 200/150/100 store credits; 50 per qualifying merged MR | upcoming Jan 2027 |

Keep these event identities, rule sets, timelines, and results separate. The October Community Hackathon edition recorded 76 prize winners and 636 merged MRs; the next event page countdown points to January 21–28, 2027. Its current rules version is 2026-10-v2.
For GitLab AI Hackathon, the rules text and connector structured start instant
differ; for Life After Code, structured judging/winner dates differ from the
rules' expected dates. The dossier records both values and the source
discrepancies. Preserve live connector timestamps as observations and retain
the published rules as their own source record.

The official event material links the GitLab Discord `#ai-hackathon`, the
Devpost Discord, office hours, GitLab Duo Agent/Flow docs, prompt library, and
the participant template. The historical group-access form is closed with
the February–March event. A future cycle must supply a fresh official
registration/access path before a registration plan advances.

The supplied DevSecOps Flow subgroup is a useful source target; its observed
empty state leaves challenge brief, active project, and owner-entry state
NOT_ESTABLISHED. The sibling `transcend` group remains a separate 312-project
source with event-cycle mapping NOT_ESTABLISHED. Keep the AI Hackathon and Transcend next editions as
future-cycle watch targets with dates `NOT_ESTABLISHED`. Owner registration,
group membership, and submission state: NOT_ESTABLISHED. The new source registry is currently an inventory only; the weekly
Challenge OSINT watcher and Devpost directory adapter remain unchanged until
their own integration work is implemented and observed.
