#!/usr/bin/env python3
"""bf-1: competing backfill method versions over the repo record corpora.
bf-strict v1 (full tuple or instance_key), bf-partial v1 (subset key),
bf-join v1 (strict + desk-feed outcome join). Emits a comparison record;
append-only history is the rule-8 version-comparison line."""
import json, glob, hashlib, pathlib, datetime, collections

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "experiments/doe/bf-1-backfill-methods/records"
FEED = ROOT / "apps/help-wanted-dashboard/data/desk-feed.json"
TUPLE = ("provider", "model", "system_prompt", "tools", "role", "moniker", "context")
ALIASES = {"model": ("model", "model_id", "model_version"), "system_prompt": ("system_prompt", "system_prompt_ref", "prompt_ref"),
           "tools": ("tools", "tools_ref"), "provider": ("provider",), "role": ("role",),
           "moniker": ("moniker",), "context": ("context",)}

def key_of(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:16]

def identity(rec):
    views = [rec]
    tr = rec.get("treatment")
    if isinstance(tr, dict):
        views.append(tr)
        if isinstance(tr.get("instance"), dict):
            views.append(tr["instance"])
    if isinstance(rec.get("instance"), dict):
        views.append(rec["instance"])
    merged = {}
    for v in views:
        for member, names in ALIASES.items():
            if member in merged:
                continue
            for n in names:
                val = v.get(n)
                if val and str(val) not in ("None", "null"):
                    merged[member] = str(val); break
    if rec.get("instance_key"):
        merged["instance_key"] = str(rec["instance_key"])
    return merged

def has_outcome(rec):
    if rec.get("status") or rec.get("outcome"):
        return True
    m = rec.get("metrics") or {}
    return any(m.get(k) is not None for k in ("first_pass_success", "rework_cycles"))

def feed_rows():
    try:
        feed = json.loads(FEED.read_text())
    except Exception:
        return []
    rows = []
    for trav in feed.get("traversals", []) or []:
        if isinstance(trav, dict):
            for r in trav.get("provider_usage", []) or []:
                if isinstance(r, dict):
                    rows.append(r)
    return rows

def main():
    files = sorted(glob.glob(str(ROOT / "experiments/doe/*/records/*.json")))
    units = []
    for f in files:
        try:
            rec = json.loads(pathlib.Path(f).read_text())
        except Exception:
            continue
        if not isinstance(rec, dict) or rec.get("campaign_id", "").startswith("bf-1"):
            continue
        units.append((pathlib.Path(f).name, rec, identity(rec)))
    strict_keys, partial_map, gold = {}, {}, []
    scored = {"bf-strict v1": 0, "bf-partial v1": 0, "bf-join v1": 0}
    outcome_filled = 0
    for name, rec, ident in units:
        full = all(ident.get(m) for m in TUPLE)
        if full or ident.get("instance_key"):
            k = ident.get("instance_key") or key_of({m: ident[m] for m in TUPLE})
            strict_keys[name] = k; scored["bf-strict v1"] += 1; scored["bf-join v1"] += 1
            gold.append((name, k, ident))
        if ident.get("provider") and ident.get("model"):
            pk = key_of({"provider": ident["provider"], "model": ident["model"], "role": ident.get("role")})
            partial_map[name] = pk; scored["bf-partial v1"] += 1
        if has_outcome(rec):
            outcome_filled += 1
    by_partial = collections.defaultdict(set)
    for name, k, ident in gold:
        if ident.get("provider") and ident.get("model"):
            pk = key_of({"provider": ident["provider"], "model": ident["model"], "role": ident.get("role")})
            by_partial[pk].add(k)
    collisions = sum(1 for v in by_partial.values() if len(v) > 1)
    rows = feed_rows()
    feed_filled = [r for r in rows if r.get("first_pass_success") is not None]
    recovered = 0
    for name, rec, ident in units:
        if has_outcome(rec) or not ident.get("provider"):
            continue
        day = str(rec.get("observed_at") or rec.get("recorded_at") or "")[:10]
        for r in rows:
            if (r.get("provider") and ident["provider"].lower() in r["provider"].lower()
                    and str(r.get("ts") or "")[:10] == day and r.get("first_pass_success") is not None):
                recovered += 1; break
    n = len(units)
    result = {
        "campaign_id": "bf-1-backfill-methods",
        "compared_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "corpus_units": n,
        "methods": {
            "bf-strict v1": {"scored": scored["bf-strict v1"], "coverage": round(scored["bf-strict v1"] / n, 4) if n else 0,
                             "distinct_keys": len(set(strict_keys.values()))},
            "bf-partial v1": {"scored": scored["bf-partial v1"], "coverage": round(scored["bf-partial v1"] / n, 4) if n else 0,
                              "distinct_keys": len(set(partial_map.values())), "collisions_on_gold": collisions,
                              "gold_units": len(gold)},
            "bf-join v1": {"scored": scored["bf-join v1"], "outcome_fills_recovered": recovered,
                           "note": "feed outcome fields are null (in flight) on all current stamps" if not feed_filled else f"{len(feed_filled)} filled feed stamps available"},
        },
        "outcome_completeness_in_corpus": round(outcome_filled / n, 4) if n else 0,
        "significance": "NOT_ESTABLISHED - corpus and per-class n far below the standing gate (n>=30/class, minority>=10, p<.05); candidates are watch-only, no cull/promote action.",
    }
    prov = {}
    try:
        audit = json.loads((ROOT / "ops/telemetry/attribution-backfill-audit.json").read_text())
        null_n = audit.get("null_actor", audit.get("null", audit.get("unattributed")))
        total = audit.get("window_prs") or audit.get("total") or audit.get("population") or (audit.get("attributed", 0) + (null_n or 0))
        prov["attribution/1"] = {"population": total, "attributed": audit.get("attributed"),
                                 "null": null_n,
                                 "attributed_rate": round(audit["attributed"] / total, 4) if total else None,
                                 "method_home": "scripts/telemetry_ingest/attribution.py (PR #3361)"}
    except Exception as e:
        prov["attribution/1"] = {"error": str(e)}
    try:
        corr = json.loads((ROOT / "ops/telemetry/token-attribution-correlation.json").read_text())
        hist = corr.get("app_action_history", [])
        prov["token_correlation"] = {"app_history_prs": sum(h.get("prs_opened", 0) for h in hist),
                                     "apps": len(hist),
                                     "note": "join-class recovery on the provenance population: PAT-era owner-login PRs redistributed to app actors by token correlation (counts in the correlation file)"}
    except Exception as e:
        prov["token_correlation"] = {"error": str(e)}
    result["provenance_corpus"] = prov
    result["cross_method_read"] = ("attribution/1 (a join-class method over a correlation source) attributes ~91% of its "
                                    "provenance population, vs ~2% strict keying on the EXPERIMENT corpus - different "
                                    "populations, not a like-for-like delta: the transferable datum is that join-class "
                                    "recovery works when a correlation source exists; the EXPERIMENT corpus has none yet.")
    OUT.mkdir(parents=True, exist_ok=True)
    prior = sorted(OUT.glob("comparison-*.json"))
    seq = (int(prior[-1].stem.split("-")[1]) + 1) if prior else 1
    (OUT / f"comparison-{seq:04d}.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT / "SUMMARY.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
