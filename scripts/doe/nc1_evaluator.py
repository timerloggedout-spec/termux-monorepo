#!/usr/bin/env python3
"""nc-1 evaluator v2 — ORDERED validation stack (Amend2, PR #2869).

Arms are ablations of the ordered stack L1 -> L2 -> L3:
  L1-only : intake validation alone
  L1+L2   : + intermittent re-verification sweep
  FULL    : + broader GitHub layer (docs/records coverage)

Layer reach (which units a layer can flag at all):
  L1: chat stratum (intake happens at relay)
  L2: chat + github (sweep re-verifies intake surfaces)
  L3: all strata (broader layer)

Detector of record: information density < tau[stratum] (Amend1,
PR #2866; records stratum uses the value-side records_density
variant — see corpus README finding #2). prose_ratio is reported
as a diagnostic only. tau comes from records/corpus/TAU-AMENDMENT
(per-stratum, pre-scoring, never tuned on scored data).

Flags are separable per layer: an optional flags file
{unit_id: {"L1": bool|null, "L2": bool|null, "L3": bool|null}}
overrides the reference-core flag for that layer/unit (Tier-1
builds plug in this way). Reference-core mode = flags generated
by the density rule inside each layer's reach; runs in this mode
are labeled mode=reference-core, and any local (non-workflow)
run is OBSERVATIONAL per DOE-FAMILY rule 5.

Cascade cost model: layers run in order; a layer scans only
units not already flagged by an earlier layer in the stack.
tokens_scanned accumulates actual scans.

escape_rate / correction_latency: computed ONLY from explicit
L1 intake verdicts in the corpus ({l1_verdict, l1_at} with
l1_evidence="explicit"). With no explicit-class units they are
NOT_ESTABLISHED (null + note) — never 0, never synthesized from
reference flags (same rule at every layer would make escape
degenerate by construction).

L1 verdict feed (main, from run-002): main emits batched digests
of intake verdicts, one row per validated handoff:
  {"chat_id": ..., "handoff_ts": ..., "verdict": "confirm|reject",
   "ts": ...}
Join key = chat_id + handoff_ts. A unit joins when its
`join_key` field equals "<chat_id>@<handoff_ts>", or when its
source_ref embeds that pair (future layer-outputs). Corpus v1
chat units carry seq-based source_refs and no join_key, so they
never join — they stay implicit/none, honestly. A joined unit
becomes explicit-class: verdict confirm -> l1_verdict "pass"
(intake accepted, no flag), reject -> "drift" (intake flagged
it; the flag time is the feed ts). correction_latency joins
only when the unit also carries `corrected_at` (latency =
corrected_at - l1_at, seconds); otherwise latency stays
NOT_ESTABLISHED even when escape_rate is established.

prose_about_notation units are excluded from binary metrics and
from tau derivation; each arm reports its flag count on the
class as a diagnostic (construct finding #1).

chat_noise_events = 0 by construction: the harness performs no
chat or GitHub writes; the rule-5 workflow posts one rollup
comment per dispatch on the tracking issue, which is the
designated channel, not chat noise.

Usage:
  nc1_evaluator.py <units.jsonl> <tau.json> [out.json]
                   [--flags flags.json] [--l1-feed feed.jsonl]
                   [--record RECORD.json
                    --master-sha <40hex> --run-id run-001]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nc1_features import features  # noqa: E402

LAYER_REACH = {
    "L1": {"chat"},
    "L2": {"chat", "github"},
    "L3": {"chat", "github", "docs", "records"},
}
ARMS = {
    "L1-only": ["L1"],
    "L1+L2": ["L1", "L2"],
    "FULL": ["L1", "L2", "L3"],
}
BINARY = ("drift", "compliant")


def reference_flag(unit, tau):
    f = features(unit["text"], unit["stratum"])
    return f["density"] < tau[unit["stratum"]]


def layer_flags(units, tau, overrides):
    """{unit_id: {layer: bool|None}} — None = layer cannot reach unit."""
    out = {}
    for u in units:
        row = {}
        for layer, reach in LAYER_REACH.items():
            if u["stratum"] not in reach:
                row[layer] = None
            elif overrides.get(u["unit_id"], {}).get(layer) is not None:
                row[layer] = bool(overrides[u["unit_id"]][layer])
            else:
                row[layer] = reference_flag(u, tau)
        out[u["unit_id"]] = row
    return out


def run_arm(units, flags, stack):
    """Cascade over the ordered stack; returns metrics + per-unit flags."""
    flagged, scanned_tokens, covered = {}, 0, set()
    for u in units:
        hit = False
        for layer in stack:
            fl = flags[u["unit_id"]][layer]
            if fl is None:
                continue
            covered.add(u["unit_id"])
            if hit:
                break  # earlier layer already flagged: later layers never scan it
            scanned_tokens += u["_tokens"]
            if fl:
                hit = True
        flagged[u["unit_id"]] = hit if u["unit_id"] in covered else None
    binary = [u for u in units if u["label"] in BINARY]
    tp = sum(1 for u in binary if flagged[u["unit_id"]] and u["label"] == "drift")
    fp = sum(1 for u in binary if flagged[u["unit_id"]] and u["label"] == "compliant")
    fn_cov = sum(1 for u in binary
                 if flagged[u["unit_id"]] is False and u["label"] == "drift")
    fn_unc = sum(1 for u in binary
                 if flagged[u["unit_id"]] is None and u["label"] == "drift")
    pan = [u for u in units if u["label"] == "prose_about_notation"]
    return {
        "units_covered": len(covered),
        "tp": tp, "fp": fp, "fn_covered": fn_cov, "fn_uncovered": fn_unc,
        "precision": round(tp / (tp + fp), 4) if tp + fp else None,
        "recall_covered": round(tp / (tp + fn_cov), 4) if tp + fn_cov else None,
        "recall_global": round(tp / (tp + fn_cov + fn_unc), 4)
                         if tp + fn_cov + fn_unc else None,
        "tokens_scanned": scanned_tokens,
        "tokens_per_confirmed_drift": round(scanned_tokens / tp, 1) if tp else None,
        "prose_about_notation_flagged": sum(1 for u in pan if flagged[u["unit_id"]]),
        "prose_about_notation_units": len(pan),
        "_flagged": flagged,
    }


def _parse_ts(s):
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def apply_l1_feed(units, feed_rows):
    """Join main's batched L1 verdict feed onto units (see module
    docstring). Mutates joined units to explicit-class and returns
    the number of joins. Feed rows may carry chat_id + handoff_ts
    or a composite unit_ref "chat_id@handoff_ts"."""
    index = {}
    for row in feed_rows:
        key = row.get("unit_ref") or (
            f"{row.get('chat_id')}@{row.get('handoff_ts')}"
            if row.get("chat_id") and row.get("handoff_ts") else None)
        if key:
            index[key] = row
    joins = 0
    for u in units:
        key = u.get("join_key")
        if not key:
            sr = str(u.get("source_ref", ""))
            for k in index:
                if k in sr:
                    key = k
                    break
        row = index.get(key) if key else None
        if not row:
            continue
        u["l1_verdict"] = "pass" if row["verdict"] == "confirm" else "drift"
        u["l1_at"] = row.get("ts")
        u["l1_evidence"] = "explicit"
        if u.get("corrected_at") and row.get("ts"):
            a, b = _parse_ts(row["ts"]), _parse_ts(u["corrected_at"])
            if a is not None and b is not None and b >= a:
                u["correction_latency_s"] = round(b - a, 1)
        joins += 1
    return joins


def escape_and_latency(units, full_flags):
    explicit = [u for u in units
                if u.get("l1_evidence") == "explicit" and u.get("l1_verdict")]
    if not explicit:
        return {"escape_rate": None, "correction_latency": None,
                "status": "NOT_ESTABLISHED",
                "note": "no explicit-class L1 verdicts in corpus; "
                        "reference-core escape would be degenerate"}
    drift = [u for u in explicit
             if u["label"] == "drift" and u["l1_verdict"] != "drift"]
    caught = [u for u in drift if full_flags.get(u["unit_id"])]
    lat = [u["correction_latency_s"] for u in explicit
           if isinstance(u.get("correction_latency_s"), (int, float))]
    lat_sorted = sorted(lat)
    return {
        "escape_rate": round(len(caught) / len(drift), 4) if drift else None,
        "correction_latency": lat_sorted[len(lat_sorted) // 2] if lat else None,
        "status": "ESTABLISHED" if drift else "NOT_ESTABLISHED",
        "note": f"explicit-class units={len(explicit)} "
                f"l1-passed-drift={len(drift)} latency_n={len(lat)}",
    }


def cull_analysis(arms):
    """DESIGN cull rule as data (verdict stays doe-expert's):
    marginal recall gain < 0.03 while marginal tokens > +25%."""
    order = [("L2", "L1-only", "L1+L2"), ("L3", "L1+L2", "FULL")]
    out = {}
    for layer, base, ext in order:
        dr = round(arms[ext]["recall_global"] - arms[base]["recall_global"], 4)
        dt = round((arms[ext]["tokens_scanned"] - arms[base]["tokens_scanned"])
                   / arms[base]["tokens_scanned"], 4) \
            if arms[base]["tokens_scanned"] else None
        out[layer] = {"delta_recall_global": dr, "delta_tokens_pct": dt,
                      "cull_rule_fires": bool(dr < 0.03 and dt is not None
                                              and dt > 0.25)}
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    opts = {argv[i][2:]: argv[i + 1] for i, a in enumerate(argv)
            if a.startswith("--") and i + 1 < len(argv)}
    units = [json.loads(l) for l in Path(args[0]).read_text().splitlines()
             if l.strip()]
    tau = json.loads(Path(args[1]).read_text())
    overrides = {}
    if "flags" in opts:
        raw = Path(opts["flags"]).read_text().strip()
        try:
            overrides = json.loads(raw)  # {unit_id: {layer: bool}} form
        except json.JSONDecodeError:  # JSONL rows (Tier-1 delivery format)
            for line in raw.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                overrides.setdefault(row["unit_id"], {})[row["layer"]] = bool(row["drift"])
    feed_joins = 0
    if "l1-feed" in opts:
        feed_rows = [json.loads(l) for l in
                     Path(opts["l1-feed"]).read_text().splitlines() if l.strip()]
        feed_joins = apply_l1_feed(units, feed_rows)
    for u in units:
        u["_tokens"] = features(u["text"], u["stratum"])["tokens"]
    flags = layer_flags(units, tau, overrides)
    arms = {name: run_arm(units, flags, stack) for name, stack in ARMS.items()}
    esc = escape_and_latency(units, arms["FULL"]["_flagged"])
    result = {
        "campaign": "nc-1-notation-compliance",
        "mode": "tier1-flags" if overrides else "reference-core",
        "tau": tau,
        "corpus_units": len(units),
        "arms": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                 for k, v in arms.items()},
        "l1_feed_joins": feed_joins,
        "escape_rate": esc["escape_rate"],
        "correction_latency": esc["correction_latency"],
        "escape_latency_status": esc["status"],
        "escape_latency_note": esc["note"],
        "cull_analysis": cull_analysis(arms),
        "pass_floor_check": {
            "precision_ge_0.90": (arms["FULL"]["precision"] or 0) >= 0.90,
            "recall_global_ge_0.80": (arms["FULL"]["recall_global"] or 0) >= 0.80,
            "chat_noise_events_eq_0": True,
            "note": "floor check is data for doe-expert's verdict, not a verdict",
        },
        "chat_noise_events": 0,
    }
    out_path = args[2] if len(args) > 2 else None
    if out_path:
        Path(out_path).write_text(json.dumps(result, indent=1))
    if "record" in opts:
        sha = opts.get("master-sha", "0" * 40)
        metrics = {}
        for arm, m in result["arms"].items():
            for k, v in m.items():
                metrics[f"{arm}.{k}"] = v
        metrics["escape_rate"] = result["escape_rate"]
        metrics["correction_latency"] = result["correction_latency"]
        metrics["chat_noise_events"] = 0
        record = {
            "schema_version": "1.0",
            "experiment_id": f"nc-1-{opts.get('run-id', 'run-001')}",
            "observed_at": opts.get("observed-at", "2026-10-31T00:00:00Z"),
            "baseline_sha": sha, "candidate_sha": sha,
            "suite": "nc-1-notation-compliance",
            "treatment": {"manager_policy_id": "nc-1-evaluator/"
                          + result["mode"], "arm": "FULL"},
            "status": "observed",
            "outcome": "scores emitted; verdict = doe-expert",
            "metrics": metrics,
            "provenance": "other", "confidence": "medium",
            "evidence_refs": [],
        }
        Path(opts["record"]).write_text(json.dumps(record, indent=1))
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
