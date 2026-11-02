#!/usr/bin/env python3
"""Density association stats for Provenance + HindSight (separate sinks).

Metric = DoE nc-1 (PR #2865, experiments/doe/nc-1-notation-compliance/
DESIGN.json, owner amendment 2026-10-31):

  information_density = signal_units / tokens, per unit, on ALL data
  surfaces. signal_units = weighted count of carried signal elements:
  identifiers (PR#/SHA/issue/session ids), decisions and verdicts,
  quantities and states, evidence refs, novel facts; minus penalties
  for restated signal, boilerplate and filler.

Operationalization (deterministic, stdlib only; an approximation of the
nc-1 definition, recorded here so the stats are reproducible):
  tokens        = whitespace-split token count of the artifact text.
  identifiers   = regex hits for #<n>, 7-40-hex SHAs, file paths, URLs,
                  and id-shaped tokens (word chars with digits/dashes).
  verdicts      = hits from a fixed decision/verdict/state word list.
  quantities    = numeric tokens (0.5 weight each).
  restatement   = tokens in exact-duplicate sentences after the first
                  occurrence (penalty 1.0 per signal-equivalent token:
                  duplicated sentence tokens / 4).
  signal_units  = identifiers + verdicts + 0.5*quantities - restatement,
                  floored at 0.
No tau is invented: nc-1 tau is set by the DoE lane from its gold corpus
before scoring. Associations here are rank-based and tau-independent.

Artifact/outcome sources:
  github stratum : PRs from a pulls-list snapshot (title+body text).
                   outcome_kind=merged (closed PRs only; open=pending,
                   excluded from association, counted). landed == merged
                   in this repo's squash-to-master flow (fleet merge rule).
  records stratum: Delphi RFP feed (title + 10 form-question responses).
                   outcome_kind=scored, outcome_value=effective_score.
                   lane = the RFP's own `lane` field.

Statistics: Spearman rho (average ranks, tie-corrected via Pearson on
ranks), two-sided p by normal approximation on the t transform.
Per-lane aggregates for lanes with n>=3. An association is ESTABLISHED
only when n>=30, both outcome classes (binary) have n>=10, and p<0.05;
otherwise NOT_ESTABLISHED with the reason. No claim ships without stats.

Outputs (separate):
  Provenance: ops/telemetry/density-stats.json (full tables + hashes)
  HindSight : ops/telemetry/density-hindsight.jsonl (one retain payload
              per lane aggregate + per association verdict)
"""
from __future__ import annotations

import argparse, hashlib, json, math, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import attribution as attribution_mod

ID_PATTERNS = [
    re.compile(r"#\d+"),
    re.compile(r"\b[0-9a-f]{7,40}\b"),
    re.compile(r"\b[\w.-]+/[\w./-]*\.\w+\b"),          # file paths
    re.compile(r"https?://\S+"),
    re.compile(r"\b\w+[-_]\w+[-_\w]*\d\w*\b"),          # id-shaped tokens
]
VERDICTS = set("""merged landed verified pass passed fail failed blocked closed open
success shipped approved rejected parked scored converged killed proven established
winner decided go nogo yes no true false""".split())
NUM_RE = re.compile(r"^\$?\d[\d,]*(\.\d+)?%?$")

def canonical(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def sha(b: bytes): return hashlib.sha256(b).hexdigest()

def signal_units(text: str):
    tokens = text.split()
    n_tokens = len(tokens)
    ident = sum(len(p.findall(text)) for p in ID_PATTERNS)
    verdicts = sum(1 for t in tokens if t.strip("`*,;:()[]{}").lower() in VERDICTS)
    quantities = sum(0.5 for t in tokens if NUM_RE.match(t.strip("`*,;:()[]{}")))
    sentences = [s.strip() for s in re.split(r"[.\n]+", text) if s.strip()]
    seen, dup_tokens = set(), 0
    for s in sentences:
        key = s.lower()
        if key in seen:
            dup_tokens += len(s.split())
        seen.add(key)
    restatement = dup_tokens / 4.0
    signal = max(0.0, ident + verdicts + quantities - restatement)
    return {"tokens": n_tokens, "identifiers": ident, "verdicts": verdicts,
            "quantities": quantities * 2, "restatement_penalty": round(restatement, 3),
            "signal_units": round(signal, 3),
            "density": round(signal / n_tokens, 6) if n_tokens else None}

def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out

def pearson(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else 0.0

def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return {"rho": None, "p_approx": None, "n": n}
    rho = pearson(ranks(xs), ranks(ys))
    if abs(rho) >= 1.0:
        p = 0.0
    else:
        t = rho * math.sqrt((n - 2) / (1 - rho * rho))
        p = math.erfc(abs(t) / math.sqrt(2))  # normal approx on t
    return {"rho": round(rho, 4), "p_approx": round(p, 6), "n": n}

def median(xs):
    s = sorted(xs); n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

def association(rows, kind):
    rows = [r for r in rows if r["density"] is not None and r["outcome_value"] is not None]
    xs = [r["density"] for r in rows]
    ys = [r["outcome_value"] for r in rows]
    sp = spearman(xs, ys)
    reasons = []
    if sp["n"] < 30:
        reasons.append(f"n={sp['n']} < 30")
    if kind == "merged":
        pos = sum(1 for y in ys if y == 1.0); neg = len(ys) - pos
        if min(pos, neg) < 10:
            reasons.append(f"minority outcome class n={min(pos, neg)} < 10")
    if sp["p_approx"] is None or sp["p_approx"] >= 0.05:
        reasons.append(f"p={sp['p_approx']} >= 0.05")
    return {"outcome_kind": kind, **sp,
            "verdict": "NOT_ESTABLISHED" if reasons else "ESTABLISHED",
            "reasons": reasons}

def build(prs, rfp_feed, generated_at, source_hashes=None, commits_by_pr=None, origin=None, files_by_pr=None):
    artifacts = []
    for pr in prs:
        text = (pr.get("title") or "") + "\n" + (pr.get("body") or "")
        d = signal_units(text)
        merged = bool(pr.get("merged_at"))
        pending = pr.get("state") == "open"
        att = attribution_mod.extract_actor(pr, (commits_by_pr or {}).get(pr["number"]), files=(files_by_pr or {}).get(pr["number"]))
        actor, keyed = attribution_mod.apply_registry(att["actor"])
        artifacts.append({"artifact_id": f"pr-{pr['number']}", "stratum": "github",
                          "lane": pr["head"]["ref"].split("/")[0] if "/" in pr["head"]["ref"] else "direct",
                          "actor": actor, "actor_evidence": att["actor_evidence"],
                          "corroboration": att.get("corroboration"),
                          "actor_registry_keyed": keyed,
                          **d, "outcome_kind": "merged",
                          "outcome_value": None if pending else (1.0 if merged else 0.0),
                          "outcome_state": "pending" if pending else ("merged" if merged else "closed_unmerged")})
    for r in rfp_feed.get("rfps", []):
        text = (r.get("title") or "") + "\n" + "\n".join(
            str(q.get("response") or "") for q in r.get("questions", []))
        d = signal_units(text)
        score = (r.get("outcome") or {}).get("effective_score")
        artifacts.append({"artifact_id": f"issue-{r['number']}", "stratum": "records",
                          "lane": r.get("lane") or "unknown", **d,
                          "outcome_kind": "scored",
                          "outcome_value": float(score) if score is not None else None,
                          "outcome_state": "scored" if score is not None else "unscored"})
    lanes = {}
    for a in artifacts:
        key = (a["stratum"], a["lane"], a["outcome_kind"])
        lanes.setdefault(key, []).append(a)
    per_lane = []
    for (stratum, lane, kind), rows in sorted(lanes.items()):
        scored = [r for r in rows if r["outcome_value"] is not None and r["density"] is not None]
        if len(rows) < 3:
            continue
        per_lane.append({"stratum": stratum, "lane": lane, "outcome_kind": kind,
                         "n": len(rows), "n_with_outcome": len(scored),
                         "density_mean": round(sum(r["density"] for r in rows) / len(rows), 6),
                         "density_median": round(median([r["density"] for r in rows]), 6),
                         "outcome_mean": round(sum(r["outcome_value"] for r in scored) / len(scored), 4) if scored else None})
    assocs = []
    for kind, stratum in (("merged", "github"), ("scored", "records")):
        rows = [a for a in artifacts if a["outcome_kind"] == kind and a["outcome_value"] is not None]
        assocs.append({"stratum": stratum, **association(rows, kind)})
    by_actor_map = {}
    for a in artifacts:
        if a["stratum"] != "github":
            continue
        by_actor_map.setdefault(a["actor"], []).append(a)
    per_actor = []
    for actor, rows in sorted(by_actor_map.items(), key=lambda kv: (kv[0] is None, kv[0] or "")):
        scored = [r for r in rows if r["outcome_value"] is not None and r["density"] is not None]
        per_actor.append({"actor": actor, "n": len(rows),
                          "corroboration": {s: sum(1 for r in rows if (r.get("corroboration") or {}).get("state") == s)
                                            for s in ("corroborated", "single-leg", "disputed")},
                          "n_with_outcome": len(scored),
                          "density_median": round(median([r["density"] for r in rows]), 6),
                          "outcome_mean": round(sum(r["outcome_value"] for r in scored) / len(scored), 4) if scored else None,
                          "evidence_methods": sorted({r["actor_evidence"]["method"] for r in rows if r["actor_evidence"]["method"]})})
    attribution_summary = {
        "method": attribution_mod.METHOD, "method_version": attribution_mod.METHOD_VERSION,
        "rule": "unknown => null, never owner-default (ACP #1241)",
        "origin": origin or {"kind": "live"},
        "github_artifacts": sum(len(v) for v in by_actor_map.values()),
        "attributed": sum(1 for a in artifacts if a.get("actor")),
        "null_actor": len(by_actor_map.get(None, [])),
        "by_evidence": {}}
    for a in artifacts:
        m = (a.get("actor_evidence") or {}).get("method")
        if m:
            attribution_summary["by_evidence"][m] = attribution_summary["by_evidence"].get(m, 0) + 1
    attribution_summary["corroboration"] = {}
    attribution_summary["disputed_artifacts"] = []
    for a in artifacts:
        st = (a.get("corroboration") or {}).get("state")
        if st:
            attribution_summary["corroboration"][st] = attribution_summary["corroboration"].get(st, 0) + 1
        if st == "disputed":
            attribution_summary["disputed_artifacts"].append(
                {"artifact_id": a["artifact_id"], "actor": a.get("actor"),
                 "conflicts": (a.get("corroboration") or {}).get("conflicts")})
    attribution_summary["scoring_rule"] = ("corroborated + single-leg reported; "
        "disputed flagged and excluded from face-value scoring (owner ruling 2026-11-01: marks != proof)")
    stats = {"schema": "telemetry-density-stats/v1",
             "metric_source": "DoE nc-1 PR #2865 DESIGN.json: information_density = signal_units / tokens (all surfaces)",
             "operationalization": "signal = identifiers + verdicts + 0.5*quantities - restatement(dup-sentence tokens/4), floor 0; tokens = whitespace split; tau NOT set here (DoE gold-corpus property)",
             "generated_at": generated_at,
             "sources": {"prs": len(prs), "rfps": len(rfp_feed.get("rfps", [])), **(source_hashes or {})},
             "artifacts": artifacts, "per_lane": per_lane, "associations": assocs,
             "per_actor": per_actor, "attribution": attribution_summary}
    stats["evidence_hash"] = sha(canonical({k: v for k, v in stats.items()}).encode())
    payloads = []
    for row in per_lane:
        content = (f"Density stats [{row['stratum']}/{row['lane']}] outcome={row['outcome_kind']} "
                   f"n={row['n']} density_median={row['density_median']} outcome_mean={row['outcome_mean']} "
                   f"evidence_hash={stats['evidence_hash']}")
        payloads.append({"schema": "telemetry-hindsight/v1", "sink": "hindsight",
                         "bank_id": "${HINDSIGHT_BANK_ID}", "content": content,
                         "metadata": {"kind": "density_lane", "lane": row["lane"],
                                      "evidence_hash": stats["evidence_hash"]}})
    for row in per_actor:
        if row["actor"] is None or row["n"] < 3:
            continue
        content = (f"Density stats [actor/{row['actor']}] outcome=merged "
                   f"n={row['n']} density_median={row['density_median']} outcome_mean={row['outcome_mean']} "
                   f"evidence={row['evidence_methods']} evidence_hash={stats['evidence_hash']}")
        payloads.append({"schema": "telemetry-hindsight/v1", "sink": "hindsight",
                         "bank_id": "${HINDSIGHT_BANK_ID}", "content": content,
                         "metadata": {"kind": "density_actor", "actor": row["actor"],
                                      "evidence_hash": stats["evidence_hash"]}})
    for a in assocs:
        content = (f"Density association [{a['stratum']}] density x {a['outcome_kind']}: "
                   f"spearman rho={a['rho']} p_approx={a['p_approx']} n={a['n']} "
                   f"verdict={a['verdict']} reasons={a['reasons']}")
        payloads.append({"schema": "telemetry-hindsight/v1", "sink": "hindsight",
                         "bank_id": "${HINDSIGHT_BANK_ID}", "content": content,
                         "metadata": {"kind": "density_association", "outcome_kind": a["outcome_kind"],
                                      "evidence_hash": stats["evidence_hash"]}})
    return stats, payloads

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prs", required=True)
    ap.add_argument("--rfp-feed", required=True)
    ap.add_argument("--now", default="1970-01-01T00:00:00Z")
    ap.add_argument("--out", default="ops/telemetry/density-stats.json")
    ap.add_argument("--hindsight-out", default="ops/telemetry/density-hindsight.jsonl")
    ap.add_argument("--files-dir", default=None,
                    help="dir of <number>.json PR file lists (manifest/frontmatter evidence leg)")
    ap.add_argument("--commits-dir", default=None,
                    help="dir of pr-<number>.json commit lists (git-author evidence leg)")
    ap.add_argument("--origin-kind", choices=["live", "backfill"], default="live")
    ap.add_argument("--origin-from", default=None)
    ap.add_argument("--origin-to", default=None)
    ap.add_argument("--audit-out", default="ops/telemetry/attribution-backfill-audit.json")
    args = ap.parse_args()
    files_by_pr = {}
    if args.files_dir:
        for f in Path(args.files_dir).glob("*.json"):
            try:
                files_by_pr[int(f.stem)] = json.loads(f.read_text())
            except Exception:
                pass
    commits_by_pr = {}
    if args.commits_dir:
        for f in Path(args.commits_dir).glob("pr-*.json"):
            commits_by_pr[int(f.stem.split("-")[1])] = json.loads(f.read_text())
    origin = {"kind": args.origin_kind}
    if args.origin_kind == "backfill":
        origin = {"kind": "backfill", "method": attribution_mod.METHOD,
                  "method_version": attribution_mod.METHOD_VERSION,
                  "from": args.origin_from, "to": args.origin_to}
    stats, payloads = build(json.loads(Path(args.prs).read_text()),
                            json.loads(Path(args.rfp_feed).read_text()), args.now,
                            {"prs_snapshot_sha256": sha(Path(args.prs).read_bytes()),
                             "rfp_feed_sha256": sha(Path(args.rfp_feed).read_bytes())},
                            commits_by_pr=commits_by_pr, origin=origin,
                            files_by_pr=files_by_pr)
    if args.origin_kind == "backfill":
        first_by_actor = {}
        for a in stats["artifacts"]:
            if a.get("actor"):
                first_by_actor.setdefault(a["actor"], [])
                if len(first_by_actor[a["actor"]]) < 5:
                    first_by_actor[a["actor"]].append(
                        {"artifact_id": a["artifact_id"], "method": a["actor_evidence"]["method"]})
        audit = {"schema": "telemetry-attribution-backfill-audit/v1",
                 "generated_at": args.now, "origin": origin,
                 "window_prs": stats["attribution"]["github_artifacts"],
                 "attributed": stats["attribution"]["attributed"],
                 "null_actor": stats["attribution"]["null_actor"],
                 "by_evidence": stats["attribution"]["by_evidence"],
                 "by_actor": {r["actor"]: r["n"] for r in stats["per_actor"] if r["actor"]},
                 "first_attributed_units": first_by_actor,
                 "stats_evidence_hash": stats["evidence_hash"]}
        Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.audit_out).write_text(json.dumps(audit, indent=1, sort_keys=True) + "\n")
        print(f"backfill audit -> {args.audit_out}: attributed={audit['attributed']} null={audit['null_actor']}")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(stats, indent=1, sort_keys=True) + "\n")
    Path(args.hindsight_out).write_text("".join(canonical(p) + "\n" for p in payloads))
    print(f"artifacts={len(stats['artifacts'])} lanes={len(stats['per_lane'])} "
          f"associations={[(a['outcome_kind'], a['rho'], a['verdict']) for a in stats['associations']]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
