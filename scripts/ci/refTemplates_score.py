#!/usr/bin/env python3
"""Score refTemplates research children into tier A–D with multi-layer fields.

Reads inventory JSONL (from refTemplates_inventory.py) or walks tree live.
Does not require network for base scores. ELO pair updates are offline stubs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF15 = ROOT / "refTemplates" / "15_Research_Repo_Templates"

# Seed ratings (1000 = baseline). Promote path still requires dual-gate.
SEED_ELO = {
    "jogyo-research-lab": 1180,
    "docxology-template": 1120,
    "yy-project-template": 1100,
    "buoyancy99-research-template": 1080,
    "yp-edu-research-project-template": 1070,
    "seunghyukoh-research-template": 1090,
    "irudik-repo-template": 1060,
    "jdingel-projecttemplate": 1050,
    "3rdCore-Research_Project_Template": 1080,
}


def score_child(name: str, has_source: bool, has_readme: bool, source_preview: str | None) -> dict:
    layers = {
        "L0_surface": 0.5 if source_preview else 0.2,
        "L1_layout": 1.0 if (has_source and has_readme) else 0.3,
        "L2_agent_surface": 0.8 if "jogyo" in name or "opencode" in (source_preview or "").lower() else 0.4,
        "L3_commit_slice": 0.0,  # filled by commit_slice script later
        "L4_deepwiki": 0.0,  # filled by deepwiki_batch later
        "L5_papers": 0.2,  # bump when 17_Papers links this slot
        "L6_actions_fit": 0.9 if has_source else 0.2,
    }
    composite = sum(layers.values()) / len(layers)
    elo = SEED_ELO.get(name, 1000)
    if composite >= 0.55 and has_source and has_readme:
        tier = "A"
    elif composite >= 0.35:
        tier = "B"
    elif composite >= 0.2:
        tier = "C"
    else:
        tier = "D"
    return {
        "name": name,
        "tier": tier,
        "elo": elo,
        "composite": round(composite, 4),
        "layers": layers,
        "has_source": has_source,
        "has_readme": has_readme,
        "source_preview": source_preview,
        "scored_at": datetime.now(UTC).isoformat(),
    }


def walk_live() -> list[dict]:
    rows: list[dict] = []
    if not REF15.is_dir():
        return rows
    for c in sorted(REF15.iterdir()):
        if not c.is_dir():
            continue
        source = c / "SOURCE.txt"
        readme = c / "README.md"
        preview = None
        if source.is_file() and source.stat().st_size:
            preview = source.read_text(encoding="utf-8").strip().splitlines()[0]
        rows.append(
            score_child(
                c.name,
                source.is_file(),
                readme.is_file(),
                preview,
            )
        )
    return rows


def from_inventory(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if not str(entry.get("slot", "")).startswith("15_"):
            continue
        for rc in entry.get("research_children", []):
            rows.append(
                score_child(
                    rc["name"],
                    bool(rc.get("has_source")),
                    bool(rc.get("has_readme")),
                    rc.get("source_preview"),
                )
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="Inventory JSONL from refTemplates_inventory")
    parser.add_argument("--output", type=Path, help="Scores JSONL out")
    args = parser.parse_args()

    rows = from_inventory(args.inventory) if args.inventory else walk_live()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
        print(f"OK: scored {len(rows)} → {args.output}")
    else:
        for r in rows:
            print(json.dumps(r, sort_keys=True))
    tiers = {}
    for r in rows:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
    print(f"OK: tier counts {tiers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
