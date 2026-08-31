# Hex × Agent Team Moneyball Integration

**Status:** integration contract / pilot implementation

**Contract:** `3l0.moneyball.v1`

## Purpose

Hex is the analytics and evidence layer for the Agent Team Moneyball system. GitHub Actions remains the execution/orchestration plane and the durable ledger must remain outside Hex when long-term audit retention is required.

The repository already has a continuous evaluation workflow that dynamically discovers eligible provider/model candidates, preserves cohort refs, invokes candidates through the HTTP LLM action, and uploads immutable evaluation manifests/telemetry artifacts. The Hex integration consumes those evidence artifacts; it does not become the execution authority.

## Data contract

Every record is associated with a GitHub Actions **run attempt**, not merely a workflow run ID. Re-runs reuse `run_id`, so `run_attempt` is mandatory for identity.

| Dataset | Grain | Primary key |
| --- | --- | --- |
| `experiment_run` | one Actions workflow run attempt × experiment arm | `run_uid = gha:{repo}:{run_id}:{run_attempt}` |
| `agent_task_attempt` | one agent × task × attempt | `attempt_uid` |
| `provider_call` | one provider/model API call | `call_uid` |
| `outcome_score` | one attempt × scorer × metric | `score_uid` |
| `manager_decision` | one orchestration policy decision event | `decision_uid` |

Required run-level dimensions:

- `run_uid`, `repo`, `gha_run_id`, `gha_run_attempt`
- full `git_sha`
- `harness_version`
- `manager_policy_id`
- `experiment_id`
- `arm`
- `contract_version = 3l0.moneyball.v1`
- `started_at`, `ended_at`, `status`, `trigger`

Required attempt-level dimensions:

- `attempt_uid`, `run_uid`, `task_id`, `agent_id`, `attempt_no`
- `terminal_state`, `retry_reason`
- `conflict_class`, `human_intervention`, `intervention_kind`

Required provider-call dimensions:

- `call_uid`, `attempt_uid`, `provider`, `model_id`, `model_version_pin`
- `http_status`, `latency_ms`, `input_tokens`, `output_tokens`, `cost_usd`
- `error_class` when HTTP status is non-success
- `rationale_hash` when a rationale fingerprint is useful

Required scoring dimensions:

- `score_uid`, `attempt_uid`, `scorer_kind`, `metric_name`
- `score_scale`, `primary_score`, `is_primary`
- `attribution_method`, `attribution_confidence`

Required manager-decision dimensions:

- `decision_uid`, `run_uid`, `manager_policy_id`, `decision_kind`
- `from_agent`, `to_agent`, `reason_code`

### Security invariant

**Never export prompts, completions, tool payloads, repository contents, provider credentials, or arbitrary log messages.** The evidence contract is metadata-first. If a legacy event contains free-form text, export only a cryptographic hash or a bounded classification derived before export.

## Canonical metrics

`raw_pass_rate = succeeded_attempts / all_attempts`

`confidence_weighted_score = SUM(primary_score * attribution_confidence) / SUM(attribution_confidence)`

`cost_per_success_usd = SUM(provider_cost_usd) / succeeded_attempts`, with null rather than zero when there are no successes.

Always display `mean_attribution_confidence` and `low_confidence_attempts` next to the confidence-weighted headline.

Retries are not failures. Human-intervened attempts require their own denominator. Provider calls must never be joined at task grain without aggregation first, or the attempt denominator will be multiplied.

## GitHub → Hex transport

### Pilot

1. GitHub Actions validates and emits contract-shaped NDJSON.
2. Actions uploads the sanitized evidence as an artifact.
3. The Hex project imports the evidence file through its file/data-source mechanism.
4. `3L0 — Contract Validation` runs the contract checks.
5. Only validated batches feed the Explorer and Scorecard.

This pilot path is deliberately explicit: the current connected Hex workspace does **not** expose a repository-owned warehouse or an existing GitHub data connection.

### Production

Use a durable warehouse/object-store landing zone:

`GitHub Actions → object storage → MONEYBALL_RAW → MONEYBALL_MART → Hex read-only connection`

Partition by `contract_version`, table, and event date. Upserts/deduplication must use the stable run/attempt/call/score/decision keys. Keep the warehouse as the system of record and Hex as the analytical/evidence presentation layer.

A Hex API trigger may be added after the landing transaction succeeds. The trigger is a refresh signal; it is not the data transport.

## Hex project topology

1. **`3L0 — Contract Validation`** — blocking data-quality checks.
2. **`3L0 — Experiment Ledger Explorer`** — parameterized evidence drill-down.
3. **`3L0 — Moneyball Scorecard`** — manager/provider/model comparison.
4. **`3L0 — Regression Watch`** — SHA/harness/model-version-aware change detection.

Recommended parameters: experiment, arm, suite, date window, manager policy, provider/model, and `min_attribution_confidence`.

## Refresh policy

- Contract validation: per evidence batch.
- Scorecard/regression: hourly plus event-triggered when production transport exists.
- Explorer: on demand.
- Long-term retention: warehouse/object storage, not Hex run history.

## Validation gates

Blocking gates:

- PK uniqueness/non-null for all five datasets.
- Enum-domain validation.
- Referential integrity across run → attempt → call/score/decision.
- Scores and attribution confidence within `[0,1]`.
- Exactly one primary score per attempt.
- Retry/intervention consistency.
- Full 40-character SHA and pinned contract version.
- Ordered run timestamps.
- Non-negative cost.
- Error classification on failed provider calls.
- No raw prompt/completion/message columns.

Production-only gates:

- **reconciliation:** emitted attempt counts equal mart counts per run;
- **freshness:** newest accepted batch is inside the configured freshness budget;
- **idempotency:** replaying a batch does not increase row counts;
- **contract drift:** unknown contract versions fail closed.

## Current environment boundary

The connected Hex workspace currently has a public/demo Snowflake connection and no repo-specific GitHub data connection or credential. Therefore the repository can safely ship the contract, sanitizer, validation workflow, and evidence artifacts now, but a durable unattended Hex feed requires external storage/warehouse and Hex connection provisioning.

No secret value belongs in this document or in the repository. Configure credentials through the relevant platform secret stores only.
