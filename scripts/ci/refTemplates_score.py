#!/usr/bin/env python3
"""Score research layouts and capability references with separate score profiles.

Research tiers describe research-template layout fitness. Capability scores describe
metadata readiness only; task efficacy remains unmeasured until a controlled run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF15 = ROOT / "refTemplates" / "15_Research_Repo_Templates"

try:
    from scripts.ci.refTemplates_inventory import inventory_entry, slots
except ModuleNotFoundError:
    from refTemplates_inventory import inventory_entry, slots

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
PIN_RE = re.compile(r"(?:/(?:commit|tree)/|@)[0-9a-f]{40}(?=$|[\s/?#),.;])|/releases/tag/v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?(?=$|[\s/?#),.;])", re.IGNORECASE)


def score_child(name: str, has_source: bool, has_readme: bool, source_preview: str | None) -> dict:
    """Existing research-template tier score; retained as its own profile."""
    layers = {
        "L0_surface": 0.5 if source_preview else 0.2,
        "L1_layout": 1.0 if (has_source and has_readme) else 0.3,
        "L2_agent_surface": 0.8 if "jogyo" in name or "opencode" in (source_preview or "").lower() else 0.4,
        "L3_commit_slice": 0.0,
        "L4_deepwiki": 0.0,
        "L5_papers": 0.2,
        "L6_actions_fit": 0.9 if has_source else 0.2,
    }
    composite = sum(layers.values()) / len(layers)
    if composite >= 0.55 and has_source and has_readme:
        tier = "A"
    elif composite >= 0.35:
        tier = "B"
    elif composite >= 0.2:
        tier = "C"
    else:
        tier = "D"
    return {
        "candidate_class": "research_template",
        "name": name,
        "tier": tier,
        "elo": SEED_ELO.get(name, 1000),
        "composite": round(composite, 4),
        "layers": layers,
        "has_source": has_source,
        "has_readme": has_readme,
        "source_preview": source_preview,
        "scored_at": datetime.now(UTC).isoformat(),
    }


def score_capability_child(child: dict) -> dict:
    """Score source/metadata readiness; report efficacy as unmeasured until controlled runs."""
    source_preview = child.get("source_preview")
    has_source = bool(child.get("has_source"))
    has_readme = bool(child.get("has_readme") or child.get("has_reference_document"))
    metadata_files = child.get("metadata_files", [])
    category = str(child.get("category", ""))
    layers = {
        "source_attribution": 1.0 if has_source else 0.0,
        "readme_contract": 1.0 if has_readme else 0.0,
        "metadata_presence": 1.0 if metadata_files else 0.0,
        "category_mapping": 1.0 if re.match(r"^\d{2}_", category) else 0.0,
        "revision_specificity": 1.0 if source_preview and PIN_RE.search(source_preview) else 0.0,
    }
    weights = {
        "source_attribution": 0.30,
        "readme_contract": 0.20,
        "metadata_presence": 0.15,
        "category_mapping": 0.15,
        "revision_specificity": 0.20,
    }
    readiness = round(sum(layers[key] * weights[key] for key in weights), 4)
    band = (
        "source_review_ready" if readiness >= 0.95
        else "metadata_candidate" if readiness >= 0.55
        else "metadata_gap"
    )
    return {
        "candidate_class": "capability_reference",
        "name": child.get("name"),
        "category": category,
        "path": child.get("path"),
        "candidate_state": child.get("candidate_state", "discovered"),
        "provenance_state": child.get("provenance_state", "unattributed"),
        "readiness_score": readiness,
        "readiness_band": band,
        "score_scope": "metadata_readiness_only",
        "layers": layers,
        "weights": weights,
        "has_source": has_source,
        "has_readme": bool(child.get("has_readme")),
        "has_reference_document": bool(child.get("has_reference_document") or child.get("has_readme")),
        "file_reference": bool(child.get("file_reference")),
        "metadata_files": metadata_files,
        "source_preview": source_preview,
        "efficacy_score": None,
        "validation_state": "unmeasured",
        "scored_at": datetime.now(UTC).isoformat(),
    }



def validate_rows(rows: list[dict]) -> list[str]:
    """Validate the score contract and keep efficacy evidence separate."""
    errors: list[str] = []
    for index, row in enumerate(rows):
        candidate_class = row.get("candidate_class")
        if candidate_class == "capability_reference":
            if row.get("score_scope") != "metadata_readiness_only":
                errors.append(f"rows[{index}]: capability score scope must be metadata_readiness_only")
            if row.get("efficacy_score") is not None:
                errors.append(f"rows[{index}]: capability efficacy must remain unmeasured")
            if row.get("validation_state") != "unmeasured":
                errors.append(f"rows[{index}]: capability validation_state must remain unmeasured")
            readiness = row.get("readiness_score")
            if not isinstance(readiness, (int, float)) or not 0.0 <= readiness <= 1.0:
                errors.append(f"rows[{index}]: readiness_score must be within 0..1")
        elif candidate_class == "research_template":
            if row.get("tier") not in {"A", "B", "C", "D"}:
                errors.append(f"rows[{index}]: research tier must be A, B, C or D")
        else:
            errors.append(f"rows[{index}]: candidate_class is unsupported")
    return errors


def from_inventory(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if str(entry.get("slot", "")).startswith("15_"):
            for child in entry.get("research_children", []):
                rows.append(score_child(
                    child["name"], bool(child.get("has_source")),
                    bool(child.get("has_readme")), child.get("source_preview")
                ))
        for child in entry.get("candidate_children", []):
            rows.append(score_capability_child(child))
    return rows


def walk_live() -> list[dict]:
    rows: list[dict] = []
    for slot in slots():
        entry = inventory_entry(slot)
        if slot.name.startswith("15_"):
            for child in entry["research_children"]:
                rows.append(score_child(
                    child["name"], child["has_source"], child["has_readme"],
                    child.get("source_preview")
                ))
        for child in entry["candidate_children"]:
            rows.append(score_capability_child(child))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="Inventory JSONL from refTemplates_inventory")
    parser.add_argument("--output", type=Path, help="Scores JSONL out")
    args = parser.parse_args()
    rows = from_inventory(args.inventory) if args.inventory else walk_live()
    failures = validate_rows(rows)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    rows.sort(key=lambda row: (
        row["candidate_class"], row.get("category", ""), row["name"]
    ))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(f"OK: scored {len(rows)} candidates → {args.output}")
    else:
        for row in rows:
            print(json.dumps(row, sort_keys=True))
    counts: dict[str, int] = {}
    for row in rows:
        key = row["candidate_class"]
        counts[key] = counts.get(key, 0) + 1
    print(f"OK: score profiles {counts}; capability efficacy remains unmeasured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
