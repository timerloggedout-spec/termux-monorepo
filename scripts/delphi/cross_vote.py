"""Oracle Method cross-vote: comparative ballots across a generated set.

Owner design parameter (2026-10-27): each generation pass emits n
candidate proposals, and they are CROSS-VOTED. Ballots are comparative
(one ballot scores every candidate in the set, 1-25 per the
DECISION-MATRIX scale), and source classes are kept separate per the
DEBATE protocol — HUMAN_COLLABORATOR, MODEL_PROVIDER, LOCAL_BASELINE —
tallied and reported separately, never merged. DRIVER_SYNTHESIS is not
a ballot. A class with no ballots is reported as zero, never filled in.

Ballot sources:
- HUMAN_COLLABORATOR / MODEL_PROVIDER: only from recorded ballot
  files supplied to this tool (a human registrar's record; a provider
  run's receipt). Absent file = zero ballots, stated in the receipt.
- LOCAL_BASELINE: a deterministic rubric comparator computed from each
  candidate's own generation profile (evidenced ratio, unverified
  count, item shape, evidence-source spread, external-dependency
  signals). It is the panel's cold comparator — labeled LOCAL_BASELINE,
  never presented as a human or model vote.

Aggregation: within LOCAL_BASELINE, each panel role's ballot is
weighted by the existing panel formula — w = base * (0.5 +
gate_pass_rate) * (elo / 1500) — using weights from the panel weights
ledger (newest JSON state) or panel.json cold-start defaults, with the
source recorded as provenance. Human/model ballots aggregate at equal
weight within their class. The ranked outcome lists each class's
ranking separately; a combined ranking (mean of per-class ranks) is
included only when more than one class cast ballots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "delphi-cross-vote/v1"
CLASSES = ("HUMAN_COLLABORATOR", "MODEL_PROVIDER", "LOCAL_BASELINE")
DEPENDENCY_WORDS = ("account", "payment", "api key", "card", "billing")
# The gate's money veto (DELPHI-ORACLE-RFP-GATE.md): a candidate that
# needs a card / auto-bills is capped at 4 by the cost auditor.
MONEY_VETO_WORDS = ("card", "billing", "payment", "auto-bill")


def _sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def candidate_profile(candidate_id: str, docs: dict[str, str],
                      brief: dict, evidence_sets: list[dict]) -> dict:
    """Deterministic generation profile the rubric comparator reads."""
    points = brief.get("summary_points", [])
    index = {}
    for ev in evidence_sets:
        for item in ev.get("items", []):
            index.setdefault(item["claim"], item)
    evidenced = sum(1 for p in points
                    if p.get("evidence_refs")
                    and all(r in index for r in p["evidence_refs"]))
    sources = {it["provenance"]["path"] for ev in evidence_sets
               for it in ev.get("items", [])}
    items = brief.get("items", [])
    item_texts = [(it.get("item", "") + " " + it.get("evidence", "")).lower()
                  for it in items]
    dependency_items = sum(1 for t in item_texts
                           if any(w in t for w in DEPENDENCY_WORDS))
    money_veto = any(any(w in t for w in MONEY_VETO_WORDS) for t in item_texts)
    return {
        "candidate": candidate_id,
        "points": len(points),
        "evidenced": evidenced,
        "unverified": len(points) - evidenced,
        "evidenced_ratio": (evidenced / len(points)) if points else 0.0,
        "items": len(items),
        "evidence_sources": len(sources),
        "dependency_items": dependency_items,
        "money_veto": money_veto,
        "docs_sha256": _sha(docs),
    }


def rubric_ballots(profiles: list[dict], roles: list[str]) -> list[dict]:
    """One LOCAL_BASELINE ballot per panel role, from the profiles.

    Each role scores all candidates 1-25 on its own dimension of the
    same profile — comparative by construction, deterministic, and
    labeled a comparator, not a vote of confidence.
    """
    def clamp(x: float) -> int:
        return max(1, min(25, round(x)))

    ballots = []
    max_sources = max((p["evidence_sources"] for p in profiles), default=1) or 1
    max_items = max((p["items"] for p in profiles), default=1) or 1
    for role in roles:
        scores = {}
        for p in profiles:
            er = p["evidenced_ratio"]
            if role == "OPERATOR":
                s = 25 * er
            elif role == "reviewer":
                s = 25 * (1 - (p["unverified"] / p["points"] if p["points"] else 1))
            elif role == "builder":
                s = 25 * (0.5 * er + 0.5 * (1 - p["items"] / (max_items + 1)))
            elif role == "Scout":
                s = 25 * (0.5 * er + 0.5 * (p["evidence_sources"] / max_sources))
            elif role == "cost_auditor":
                s = 25 * (er - 0.25 * p["dependency_items"])
                if p.get("money_veto"):
                    s = min(s, 4)  # the gate's money veto, applied as scored
            else:
                s = 25 * er
            scores[p["candidate"]] = clamp(s)
        ballots.append({"voter": f"rubric:{role}", "source_class": "LOCAL_BASELINE",
                        "scores": scores})
    return ballots


def validate_ballots(ballots: list[dict]) -> None:
    """DEBATE protocol intake rules for supplied ballots.

    Every ballot names its voter. A MODEL_PROVIDER ballot is an
    experimental observation, admissible only with its run record —
    provider, model/version, run ID, response hash — and an
    entitlement basis (history: model ballots stay disabled until a
    no-cost entitlement + quota admission are validated; the basis is
    recorded, never assumed). Ballots deduplicate on
    (source_class, voter, run_id): a second ballot under the same key
    is a duplicate submission, refused.
    """
    seen: set[tuple] = set()
    for ballot in ballots:
        voter = ballot.get("voter")
        if not voter:
            raise ValueError("ballot without a voter identity")
        run = ballot.get("run") or {}
        if ballot.get("source_class") == "MODEL_PROVIDER":
            missing = [k for k in ("provider", "model", "run_id",
                                   "response_hash", "entitlement")
                       if not run.get(k)]
            if missing:
                raise ValueError(
                    f"MODEL_PROVIDER ballot from {voter!r} lacks run record "
                    f"fields: {missing}")
        key = (ballot.get("source_class"), voter, run.get("run_id"))
        if key in seen:
            raise ValueError(f"duplicate ballot (dedupe key): {key}")
        seen.add(key)


def role_weight(role_cfg: dict) -> float:
    return (role_cfg.get("base", 1.0)
            * (0.5 + role_cfg.get("gate_pass_rate", 0.5))
            * (role_cfg.get("elo", 1500) / 1500.0))


def aggregate(ballots: list[dict], weights: dict[str, float] | None = None) -> dict:
    """Weighted mean score per candidate for one class's ballots."""
    totals: dict[str, float] = {}
    weight_sum: dict[str, float] = {}
    for ballot in ballots:
        w = 1.0
        if weights:
            voter_role = ballot["voter"].split(":", 1)[-1]
            w = weights.get(voter_role, 1.0)
        for cand, score in ballot["scores"].items():
            totals[cand] = totals.get(cand, 0.0) + w * score
            weight_sum[cand] = weight_sum.get(cand, 0.0) + w
    return {cand: totals[cand] / weight_sum[cand] for cand in totals}


def rank(scores: dict[str, float]) -> list[str]:
    return sorted(scores, key=lambda c: (-scores[c], c))


def cross_vote(candidates: list[dict], panel_roles_cfg: dict,
               weights_source: str,
               extra_ballots: list[dict] | None = None,
               generated_at: str | None = None) -> dict:
    """candidates: [{id, profile}] — returns the BALLOT receipt dict."""
    generated_at = generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    extra_ballots = extra_ballots or []
    for ballot in extra_ballots:
        if ballot.get("source_class") not in CLASSES:
            raise ValueError(f"ballot with unaccepted source_class: "
                             f"{ballot.get('source_class')!r} "
                             f"(DRIVER_SYNTHESIS is not a ballot)")

    validate_ballots(extra_ballots)
    profiles = [c["profile"] for c in candidates]
    roles = list(panel_roles_cfg.keys())
    baseline = rubric_ballots(profiles, roles)
    weights = {role: role_weight(cfg) for role, cfg in panel_roles_cfg.items()}

    by_class: dict[str, list[dict]] = {cls: [] for cls in CLASSES}
    by_class["LOCAL_BASELINE"] = baseline
    for ballot in extra_ballots:
        by_class[ballot["source_class"]].append(ballot)

    per_class = {}
    for cls, ballots in by_class.items():
        if not ballots:
            per_class[cls] = {"ballots": 0, "scores": {}, "ranking": []}
            continue
        w = weights if cls == "LOCAL_BASELINE" else None
        scores = aggregate(ballots, w)
        per_class[cls] = {"ballots": len(ballots),
                          "scores": {k: round(v, 3) for k, v in scores.items()},
                          "ranking": rank(scores)}

    present = [cls for cls in CLASSES if per_class[cls]["ballots"] > 0]
    combined = None
    if len(present) > 1:
        rank_sum: dict[str, float] = {}
        for cls in present:
            for pos, cand in enumerate(per_class[cls]["ranking"], start=1):
                rank_sum[cand] = rank_sum.get(cand, 0.0) + pos
        combined = sorted(rank_sum, key=lambda c: (rank_sum[c] / len(present), c))
    primary = combined or (per_class[present[0]]["ranking"] if present else [])

    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "candidates": [c["id"] for c in candidates],
        "profiles": profiles,
        "weights": {"source": weights_source,
                    "role_weights": {k: round(v, 4) for k, v in weights.items()}},
        "ballots": baseline + extra_ballots,
        "ballots_by_class": {cls: per_class[cls]["ballots"] for cls in CLASSES},
        "per_class": per_class,
        "classes_present": present,
        "classes_absent": [cls for cls in CLASSES if cls not in present],
        "combined_ranking": combined,
        "ranked_outcome": primary,
        "class_rule": "Source classes tallied and reported separately, never "
                      "merged (DEBATE protocol). DRIVER_SYNTHESIS is not a ballot.",
    }


def load_ledger_weights(ledger_comments: list[dict]) -> dict | None:
    """Newest `delphi-weights v1` JSON state from ledger issue comments."""
    newest = None
    for comment in ledger_comments:
        body = comment.get("body") or ""
        if "<!-- delphi-weights" not in body:
            continue
        m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
        if m:
            newest = json.loads(m.group(1))
    return newest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Oracle Method cross-vote")
    parser.add_argument("--pass-dir", required=True,
                        help="pass directory written by generate_proposal --pass")
    parser.add_argument("--panel", required=True, help="panel.json path")
    parser.add_argument("--weights-file",
                        help="ledger weights JSON ({roles: {...}}); defaults to panel.json")
    parser.add_argument("--ballots-file", action="append", default=[],
                        help="recorded HUMAN_COLLABORATOR / MODEL_PROVIDER ballots JSON")
    parser.add_argument("--out", required=True, help="BALLOT.json output path")
    args = parser.parse_args(argv)

    pass_dir = Path(args.pass_dir)
    pass_meta = json.loads((pass_dir / "pass.json").read_text())
    panel = json.loads(Path(args.panel).read_text())
    roles_cfg = panel["roles"]
    weights_source = "panel.json cold-start defaults"
    if args.weights_file:
        ledger = json.loads(Path(args.weights_file).read_text())
        if ledger and ledger.get("roles"):
            roles_cfg = ledger["roles"]
            weights_source = f"ledger weights file {args.weights_file}"

    extra = []
    for bf in args.ballots_file:
        data = json.loads(Path(bf).read_text())
        extra.extend(data if isinstance(data, list) else [data])

    candidates = [{"id": c["id"], "profile": c["profile"]}
                  for c in pass_meta["candidates"]]
    receipt = cross_vote(candidates, roles_cfg, weights_source, extra)
    receipt["pass_id"] = pass_meta["pass_id"]
    Path(args.out).write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"cross-vote: ranked {receipt['ranked_outcome']} "
          f"(classes present: {receipt['classes_present']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
