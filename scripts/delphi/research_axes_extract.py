#!/usr/bin/env python3
"""Research-silo comparison-axes extractor — cycle records.

Produces ops/delphi/research-axes.json (delphi.research-axes.v1), the
post-hoc axes record the silo spec (docs/ops/RESEARCH-SILO-DELPHI.md)
names as the comparison home alongside the outcomes ledger #1487.
The gate never scores these axes; this record states, per silo and
per axis, what the cycle has actually produced — with evidence —
including the honest negative states. Feature extraction reads the
fleet's curated in-repo record of each template (the stub README +
SOURCE.txt under refTemplates/15_Research_Repo_Templates/); the
template sources themselves are not vendored (metadata-first), and
the record says so.

Usage: research_axes_extract.py [--cycle N] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "refTemplates" / "15_Research_Repo_Templates"


def _summary_and_features(readme: str) -> tuple[str, list[str], str]:
    lines = [l.rstrip() for l in readme.splitlines()]
    bullets = [re.sub(r"^-\s+", "", l).strip()
               for l in lines if l.startswith("- ")]
    para, started = [], False
    for l in lines[1:]:
        if l.startswith("#"):
            if started:
                break
            continue
        if l.strip():
            started = True
            para.append(l.strip())
        elif started:
            break
    summary = " ".join(para)
    if bullets:
        return summary, bullets, "readme_bullets"
    phrases = [p.strip() for p in re.split(r";\s*|,\s+", summary)
               if p.strip()]
    return summary, phrases, "readme_summary_phrases"


def build(cycle: int) -> dict:
    silos = json.loads(
        (ROOT / "ops/delphi/research-silos.json").read_text())["silos"]
    feed = json.loads((ROOT / "apps/help-wanted-dashboard/data/"
                            "delphi-rfp-feed.json").read_text())
    baseline_no = {r["silo"]: r["number"] for r in feed["rfps"]
                   if r["group"] == "research-baseline"}
    out = {}
    for silo in silos:
        slot_dir = BASE / silo["path"].split("/")[-1]
        readme = (slot_dir / "README.md").read_text()
        source = (slot_dir / "SOURCE.txt").read_text()
        upstream = next((l.strip() for l in source.splitlines()
                         if l.strip().startswith("https://")), None)
        summary, features, method = _summary_and_features(readme)
        n = baseline_no.get(silo["slot"])
        out[silo["id"]] = {
            "baseline_issue": n,
            "produced_output_results_validated": {
                "state": "none_validated_yet",
                "note": "Cycle-1 produced outputs of this silo stream are "
                        "the Delphi filing + gate outcome (admission "
                        "only). No silo-produced research output has "
                        "been validated yet.",
                "evidence": [f"issue #{n} (baseline RFP, gate ledger: "
                             "parked, effective 6.69/25)"],
            },
            "feature_extractions": {
                "state": "recorded",
                "method": method,
                "source": "in-repo curated record (stub README + "
                          "SOURCE.txt); template source not vendored "
                          "(metadata-first)",
                "upstream": upstream,
                "summary": summary,
                "features": features,
            },
            "consensus_implementation": {
                "state": "none_yet",
                "note": "Consensus implementation is cycle stage 6, "
                        "after variant comparison; no cross-silo "
                        "consensus implementation exists yet.",
                "evidence": ["docs/ops/RESEARCH-SILO-DELPHI.md "
                             "(baseline_cycle stage order)"],
            },
        }
    return {
        "schema": "delphi.research-axes.v1",
        "cycle": cycle,
        "recorded_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "recorded_by": "[MUSEai]@{role:{doe-expert}}",
        "generator": "scripts/delphi/research_axes_extract.py",
        "honesty_rules": [
            "Axes are post-hoc records, never gate scores (silo spec).",
            "A negative state (none_validated_yet / none_yet) is a "
            "recorded finding, not a pending placeholder.",
            "Features are verbatim from the in-repo curated record; "
            "nothing is extracted from sources the repo does not hold.",
        ],
        "silos": out,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", type=int, default=1)
    ap.add_argument("--out", default=str(
        ROOT / "ops/delphi/research-axes.json"))
    a = ap.parse_args()
    rec = build(a.cycle)
    Path(a.out).write_text(json.dumps(rec, indent=1) + "\n")
    print(f"wrote {a.out}: {len(rec['silos'])} silos, cycle {a.cycle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
