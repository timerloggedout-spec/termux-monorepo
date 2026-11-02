# Density Association Stats — Provenance + HindSight

Owner input 2026-10-31 (via main): per artifact/lane, information-density
× outcome associations, so density↔effectiveness claims carry stats,
not vibes. Source metric = DoE nc-1 (PR #2865,
`experiments/doe/nc-1-notation-compliance/DESIGN.json`).

## Metric (nc-1, verbatim definition)

`information_density = signal_units / tokens` per unit, on ALL data
surfaces (chat, GitHub, docs, records). signal_units = weighted count of
carried signal elements: identifiers (PR#/SHA/issue/session ids),
decisions and verdicts, quantities and states, evidence refs, novel
facts; minus penalties for restated signal, boilerplate and filler.

Operationalization in `scripts/telemetry_ingest/density_stats.py`
(deterministic, stdlib only, reproducible — an approximation, recorded
as such): tokens = whitespace split; identifiers = regex hits (#n,
7–40-hex SHAs, file paths, URLs, id-shaped tokens); verdicts = fixed
decision/state word list; quantities = numeric tokens ×0.5; restatement
penalty = exact-duplicate-sentence tokens / 4; signal floored at 0.
No tau is set here: nc-1 tau is a DoE gold-corpus property, set before
their scoring. Associations below are rank-based and tau-independent.

## Tables

Provenance sink (separate): `ops/telemetry/density-stats.json`
(`telemetry-density-stats/v1`, `evidence_hash` over the table):

- `artifacts[]` — per artifact: id, stratum, lane, tokens, signal
  breakdown, density, outcome_kind, outcome_value, outcome_state.
  - github stratum: PRs (title+body). outcome = `merged`
    (closed PRs only; open = `pending`, excluded from association).
    landed ≡ merged under this repo's squash-to-master merge rule.
  - records stratum: Delphi RFPs (title + form-question responses,
    from `delphi-rfp-feed.json`). outcome = `scored`,
    value = gate `effective_score`. lane = the RFP's own lane field.
- `per_lane[]` — per (stratum, lane, outcome_kind), n≥3: n,
  density mean/median, outcome mean.
- `associations[]` — per outcome_kind: Spearman rho (density ×
  outcome), two-sided p (normal approx on the t transform), n, verdict.

HindSight sink (separate): `ops/telemetry/density-hindsight.jsonl` —
one retain payload per per-lane row + per association verdict, in the
same client contract as the telemetry ingest payloads. Neither sink
feeds the other.

## Verdict rule (stats, not vibes)

An association is `ESTABLISHED` only if n≥30 AND (binary outcomes)
minority class n≥10 AND p<0.05. Otherwise `NOT_ESTABLISHED` with every
failed condition named in `reasons`. A NOT_ESTABLISHED verdict is the
honest current state of the density↔effectiveness claim — it may not be
quoted as an effect in either direction.

First table (2026-10-31, 600 most recent PRs + 28 scored RFPs):
- merged: rho ≈ −0.01, p ≈ 0.80, n=543 → NOT_ESTABLISHED.
- scored: rho ≈ −0.15, p ≈ 0.43, n=28 → NOT_ESTABLISHED (n<30, p≥0.05).

## Refresh

```
gh api "repos/{owner}/{repo}/pulls?state=all&per_page=100&page=N" (N=1..6) > prs.json
python3 scripts/telemetry_ingest/density_stats.py \
  --prs prs.json --rfp-feed apps/tribute-dashboard/data/delphi-rfp-feed.json \
  --now <ISO8601>
python3 -m pytest tests/test_density_stats.py -q
```

The `telemetry-ingest` workflow runs this on its cadence with the
workflow token and proposes the tables in the same refresh PR.

## Actor attribution (2026-11-01, attribution/1)

Every github artifact carries `actor` + `actor_evidence`, extracted by
`scripts/telemetry_ingest/attribution.py` per the
agent-contributor-provenance rules (#1241): GitHub's login names the
PAT holder, NOT the author. Evidence chain, strongest first:
`stamp` ([MUSEai]@{role:{X}}) -> `trailer` (Agent:/Signed-off-by: in
body or commit messages) -> `git_author` (known-identity mapping only)
-> `app_bot` (`*[bot]` login). No evidence => `actor: null` — never
defaulted to the owner. Registry keying: actor ids are canonicalized
through the Role{Moniker} registry where a registered entry exists
(Grok -> `Grok`, PR #3355; note `Grok (OPERATOR)` signings are the
human owner's row, not the collaborator).

Backfill over the 599-PR window (2026-10-31T16:43Z -> 2026-11-01T23:50Z) ran under
the backfill doctrine: origin-marked in the stats output
(`attribution.origin = backfill{method, method_version, from, to}`)
and audited in `ops/telemetry/attribution-backfill-audit.json`:
546/599 attributed (stamp 297, app_bot 249), 53 null. Grok units in
window: 0 — no in-window artifact carries Grok's established identity
marks; attribution is live for its post-registration work.
