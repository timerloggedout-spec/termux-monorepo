#!/usr/bin/env python3
"""CMP-1 longitudinal census: SKILL.md vs *.skill artifacts in this repo.
Emits one records/ line per run: the format-adoption curve over time."""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "experiments/doe/cmp-register/records"

def main():
    skill_md = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("SKILL.md")
                      if ".git" not in p.parts)
    dot_skill = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.skill")
                       if ".git" not in p.parts)
    rec = {"campaign_id": "cmp-register", "entry": "CMP-1",
           "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "skill_md_count": len(skill_md), "dot_skill_count": len(dot_skill),
           "dot_skill_paths": dot_skill[:50]}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "cmp1-census.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
