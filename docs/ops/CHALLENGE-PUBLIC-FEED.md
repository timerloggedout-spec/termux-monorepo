# Public Challenge Feed — contract

Schema: `challenge-public-feed/v1`
Artifact: `apps/tribute-dashboard/data/challenge-public-feed.json`
Source of truth: `ops/challenge/coordinator.json`
Generator: `scripts/dashboards/challenge_public_feed.py`
Refresh: `.github/workflows/challenge-countdowns-feed-collect.yml`
Consumer: Hackathon Desk browser module

## Trust boundary

The browser consumes the generated dashboard artifact. It does not fetch
`ops/challenge/coordinator.json`.

The generator builds every event from a fixed allowlist. It omits arbitrary
coordinator extensions, project records, opportunity-cost records, manager
ownership/evidence details, registration evidence, submission confirmation
references, and internal estimates. The serialized artifact is scanned
recursively for `metrics_internal` and `win_probability`; either key fails
generation and the contract tests.

## Envelope

- `schema`: `challenge-public-feed/v1`.
- `generated_at`: UTC generation instant.
- `source`: canonical coordinator path.
- `coordinator_schema_version`: supported source schema version.
- `events[]`: allowlisted public event records, retaining source order.

## Event allowlist

Identity and event context: `id`, `name`, `host`, `platform`,
`also_platforms`, `official_url`, `source_url`, `status`, `format`,
`kind`, `league_window`, `fetched_at`, `rules_state`, and
`claim_gate`.

Dates retain recorded strings or the `at`, `tz`, and `source` members of
date objects. The allowlist includes the ordinary event date keys and the
C12-specific `register_build`, `preliminary_due`, `finalists_announced`,
`final_due`, and `winners` keys. Top-level `deadline` is retained for
records such as C11.

C11's M1–M6 match list retains `id`, `name`, `points`, `state`,
`tasks`, `rules`, `deadline`, and `dates`. Internal queue and provenance
fields are omitted. This preserves the selectable AMD AI League event and its
match descriptions without copying its internal coordination records.

Other public fields: organizer name/role/source, constraints, gate id/label/
blocks/status/state/text, prize status/pool/source/notes/tiers, registration
state, and submission state/time. Gate ownership/evidence and submission
confirmation references remain excluded.

## Refresh and deployment

The existing challenge-countdowns collector runs both the countdown collector
and this projection generator. It proposes both dashboard JSON artifacts in
one refresh PR. The Tribute deployment copies the dashboard tree, so the
projection ships with the page.

The separate `apps/tribute-dashboard/data/dispatch-state-feed.json` is empty
on master and is not a browser dependency. The Hackathon Desk reads the
`dispatch_claims` projection embedded in the QUE queue feed.

## Failure behavior

- Unsupported coordinator schema, missing source, malformed JSON, or invalid
  event records fail generation.
- Missing, malformed, or stale browser feeds render explicit unavailable or
  stale states.
- The public artifact remains a projection; coordinator authority stays with
  the existing challenge entries lane.
