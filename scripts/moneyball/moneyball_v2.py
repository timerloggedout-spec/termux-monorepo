"""MoneyBall validators: v1 records as they exist, and the competing v2
decision-opportunity score record (docs/schemas/moneyball-score.schema.json).

Stdlib only. v1 validation describes what the landed schemas actually
guarantee; v2 validation enforces what the charter (docs/ops/
MONEYBALL-PLANE.md) promises but v1 records cannot express:

- a score belongs to an opportunity (entity x action x context x time),
  not to an entity alone;
- every axis value carries evidence refs + evidence strength;
- weights are named per pass and fixed at a named intake, summing to 1;
- the composite is recomputed, never trusted;
- capability / forecast / incremental_effect / value / surplus /
  portfolio_marginal_contribution are separate fields, and a null
  incremental_effect (unidentified) is valid and visible;
- the ballot aggregate is beside the score, never merged;
- point-in-time fields support replay eligibility checks.
"""
from __future__ import annotations

TOL = 0.05


def validate_v1_pass(pass_json: dict) -> list[str]:
    """What oracle-method-pass/v1 actually guarantees about MoneyBall:
    a candidate -> bare-number map. Returns problems (empty = valid v1)."""
    problems = []
    if pass_json.get("schema") != "oracle-method-pass/v1":
        problems.append("schema is not oracle-method-pass/v1")
    mw = pass_json.get("moneyball_weighted")
    if mw is not None:
        if not isinstance(mw, dict):
            problems.append("moneyball_weighted is not a map")
        else:
            for k, v in mw.items():
                if not isinstance(v, (int, float)):
                    problems.append(f"moneyball_weighted[{k}] is not a number")
    return problems


def v1_explanation_fields(pass_json: dict) -> set[str]:
    """Explanation content a v1 pass record carries for a MoneyBall score."""
    fields = set()
    if "moneyball_weighted" in pass_json:
        fields.add("composite")
    return fields


def composite(weights: dict[str, float], axes: list[dict]) -> float:
    return sum(weights[a["axis"]] * a["value"] for a in axes)


def validate_v2(rec: dict) -> list[str]:
    problems = []
    if rec.get("schema") != "moneyball-plane/v2":
        problems.append("schema is not moneyball-plane/v2")
    opp = rec.get("opportunity") or {}
    for f in ("entity_id", "action", "context", "decision_time"):
        if not opp.get(f):
            problems.append(f"opportunity.{f} missing")
    if not rec.get("baseline_id"):
        problems.append("baseline_id missing")
    w = rec.get("weights") or {}
    if not w.get("fixed_at"):
        problems.append("weights.fixed_at missing (per-pass intake fix not named)")
    axes_w = w.get("axes") or {}
    if not axes_w or abs(sum(axes_w.values()) - 1.0) > 1e-9:
        problems.append("weights.axes must be non-empty and sum to 1")
    axes = rec.get("axes") or []
    if not axes:
        problems.append("axes missing (a bare number is not a result)")
    for a in axes:
        if a.get("axis") not in axes_w:
            problems.append(f"axis {a.get('axis')!r} has no weight")
        if not a.get("evidence_refs"):
            problems.append(f"axis {a.get('axis')!r} has no evidence_refs")
        if a.get("evidence_strength") not in ("evidenced", "limited", "unverified"):
            problems.append(f"axis {a.get('axis')!r} evidence_strength invalid")
        v = a.get("value")
        if not isinstance(v, (int, float)) or not 0 <= v <= 10:
            problems.append(f"axis {a.get('axis')!r} value out of range 0..10")
    if axes and axes_w and not problems:
        if abs(composite(axes_w, axes) - float(rec.get("composite", -1))) > TOL:
            problems.append("composite does not match sum(weights x axis values)")
    q = rec.get("quantities")
    if not isinstance(q, dict):
        problems.append("quantities missing")
    else:
        for f in ("capability", "forecast", "incremental_effect", "value",
                  "surplus", "portfolio_marginal_contribution"):
            if f not in q:
                problems.append(f"quantities.{f} absent (must be present; null = unidentified)")
    b = rec.get("ballot") or {}
    if b.get("relation") != "beside_never_merged":
        problems.append("ballot.relation must be beside_never_merged")
    pit = rec.get("point_in_time") or {}
    for f in ("event_time", "published_at", "ingested_at"):
        if not pit.get(f):
            problems.append(f"point_in_time.{f} missing")
    if pit.get("published_at") and pit.get("ingested_at") and opp.get("decision_time"):
        if pit["published_at"] > opp["decision_time"] or pit["ingested_at"] > opp["decision_time"]:
            problems.append("point-in-time violation: evidence not available at decision_time")
    return problems


def ranking(records: list[dict]) -> list[str]:
    """Order record_ids by composite desc; identical profiles stay tied
    (stable order within a tie, tie flagged by equal composite)."""
    return [r["record_id"] for r in sorted(records, key=lambda r: -float(r["composite"]))]
