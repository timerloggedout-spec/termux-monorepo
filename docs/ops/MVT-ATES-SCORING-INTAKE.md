# MVT / ATES Scoring Intake — what routed dispatch must emit

Owner routing update (2026-11-01, via main): dispatch routing (Swarm,
`optimizations-assurance`) is being updated so **MVT/ATES scoring is
populated from live routed work across all arms**. This is the intake
contract for that population: the fields and format the scoring side
(this spec's owner, the surface-separation lane) consumes. Separation
still governs: `docs/ops/MVT-DOE-ATES-SEPARATION.md` (surfaces),
`docs/ops/DOE-FAMILY.md` (campaign doctrine). Schemas are the record
contracts — this doc names the fields; it does not fork them.

## Unit of intake

One EXPERIMENT record per dispatched arm run (cohort × task × arm ×
repetition), conforming to `docs/ops/corpus/EXPERIMENT.schema.json`
(schema_version `1.0`; rev 1.1 slots `session_id` / `window` /
`usage{}` allowed). Records are committed under the campaign's home
(`experiments/doe/<campaign>/records/`) by PR — feeds and scoring
read committed records only, never chat reports or run conclusions.

## Required fields (schema-required, scoring reads all of them)

| Field | Format / rule |
|---|---|
| `schema_version` | `"1.0"` |
| `experiment_id` | campaign/dispatch id (one id per designed comparison) |
| `observed_at` | ISO date-time of the run's observation |
| `baseline_sha` / `candidate_sha` | 40-hex; the two refs the arm compared |
| `suite` | suite id the arm ran |
| `cohort` | cohort/version id; a route or design change = a NEW cohort |
| `treatment.manager_policy_id` | routing/manager policy that dispatched the arm |
| `treatment.provider` / `treatment.model` | the RESOLVED route, stamped post-hoc (dispatch is route-parameterized; a record never carries a pre-pinned model as its result) |
| `treatment.arm` | arm id within the comparison |
| `treatment.instance` | full configured-instance stamp: {provider, model@version verbatim, system_prompt {ref, sha256}, tools {ref, sha256}, role, moniker, context, instance_key} — `instance_key` = sha256 per `scripts/doe/instance_key.py` |
| `status` | enum: observed / running / passed / failed / skipped / blocked / superseded — scoring consumes terminal rows (passed/failed/observed/skipped/blocked); `running` rows are in-flight, not scored |
| `outcome` | free-string outcome summary or null |
| `provenance` | `github` for routed dispatch records |
| `confidence` | high / medium / low |
| `evidence_refs` | URIs to the run's evidence (workflow run, session, artifact) |
| `session_id`, `window {start,end}`, `usage {status, value, unit, source}` | rev 1.1 slots; `usage.value` MUST be null when status is `activity_only` or `not_established` — no invented consumption |

## Scoring fields — `metrics{}` (this is what populates MVT/ATES scoring)

ATES trace fields (contract: `docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json`),
carried in the record's `metrics` object with these exact names:

| metrics key | Format / rule |
|---|---|
| `ates_outcome` | PASS / FAIL_DETERMINISTIC / INCONCLUSIVE / BLOCKED |
| `deterministic_score` | number [0,1] or null |
| `judge_score` | number [0,1] or null; present ONLY when scored by an evaluator instance ≠ builder instance (distinct `instance_key`, ≠ provider) — a builder's self-score is not a judge score |
| `judge_weight` | number [0, 0.3] or null |
| `net_score` | number or null |
| `wrong_commit_penalty` | number ≥ 0 |
| `trace_id` | 32-hex ATES trace id for the run |
| `task_fingerprint` / `environment_fingerprint` | 64-hex; part of the row identity join |

MVT fields: the comparison structure itself — `experiment_id` +
`cohort` + `treatment.arm` + repetition (in `metrics.repetition`)
across all arms of the design. Desk-dispatch sets (3 arms per
trigger, stop-when-conclusive, +1 set on split, cap n=12) arrive as
successive cohorts under one `experiment_id`; scoring aggregates per
cohort, then across cohorts, grouped by `instance_key` — never by
model alone.

## Honesty rules (binding on intake)

- A missing scoring field renders the row **unscored** for that
  metric — absent, never synthesized, never defaulted.
- Undesigned/extra routed runs are recorded with their real status
  and cohort; they are never retro-dressed as designed arms.
- Filters/labels in a dispatch brief are routing inputs, not
  evidence: the record's resolved instance is what scoring sees.
- Culls and 🍒-pick propagations are design events in the campaign
  record (DOE-FAMILY doctrine), not edits to prior rows.

## Backfill doctrine (owner, 2026-11-01)

Applies at every **scoring version change** (any change to the
scoring keys, their derivation, the trace contract's use, or the
aggregation above):

- **Backfill**: prior committed records are re-scored under the new
  version; a version change never leaves older cohorts scored only
  under a retired method while newer ones use the new.
- **Audited ∧ improved**: each backfill is audited (records re-read,
  deltas between versions explained in the campaign record) and the
  scoring method is improved from what the audit shows — backfill is
  a method-revision event, not a silent recompute.
- **Continuous comparison**: results under successive scoring
  versions are compared continuously (per cohort, per instance_key)
  until **DoE culling retires a method version** — retirement is a
  recorded culling event (DOE-FAMILY doctrine); a retired version's
  results stay in the record, labeled with their version, never
  overwritten in place.

Canonical record for this doctrine: the DoE expert lane's family
record (`docs/ops/DOE-FAMILY.md`); this section states its
application to MVT/ATES intake.

## Attribution corroboration — rule 9 (owner, 2026-11-01)

Canonical: DOE-FAMILY rule 9 ∧ DOE-SCORING-INTAKE §Attribution
corroboration (PR #3468). Application to this intake: a record that
carries actor attribution names its basis in `metrics` (scalar keys,
per the schema's metrics value types):

| metrics key | Format / rule |
|---|---|
| `attribution_actor` | actor the row is attributed to |
| `attribution_legs` | comma-joined legs from the evidence chain {stamp, trailer, manifest, git_author, app_bot} |
| `attribution_corroborated` | `"true"` / `"false"` — true = ≥2 independent legs agree, or Telemetry's provenance-corroboration verdict |

Rules: **population and outcome scoring are unaffected** — records
stand as records. **Actor-keyed weighting** (per-actor / per-instance
roll-ups) consumes only corroborated attribution: a single-leg mark
is UNCORROBORATED — held out of actor weights and flagged, never
taken at face value (some signings are false). A record with no
attribution keys claims no attribution (neither false nor
corroborated). Current consequence: rows whose only attribution leg
is their instance stamp (e.g. the routed-dispatch build-wire set)
count fully for population/outcome and are held out of actor
weighting until a second leg lands.

## Population check (how "populated" is judged)

Scoring shows populated when, for a campaign, committed records exist
for every dispatched arm with terminal status ∧ the `metrics` scoring
keys above present (null only where the trace contract allows null).
The separation lane verifies population from the committed records
and reports it; run counts from the Actions API alone do not count
as scoring population.

**Roll-up counting** (leveling, owner 2026-11-01; canonical in
`docs/ops/DOE-FAMILY.md`): MVT and ATES are pieces nested in the DoE
family — any population or scoring roll-up that spans surfaces
counts **DoE once**, with MVT shown as its sub-piece, never as a
separate plane tally added on top of the family count.
