#!/usr/bin/env python3
"""Harvest the g4f-working provider lists into a canonical catalog.

Source: timerloggedout-spec/g4f-working_fork (a fork of the g4f-working
list of working no-auth providers/models from xtekky/gpt4free).
Lists harvested, programmatically, with no manual transcription:
  - provider/providers_models.json  (provider -> provider_info + models)
  - working/working_results.txt     (provider|model|type, tester-verified)
  - working/test_results.json       (tester summary counts)

Output: data/g4f-working/providers.json (schema g4f-working-catalog-v1).
Discovery/reference only: harvesting a list entry never authorizes
fetching, execution, or inference against that provider (mirrors the
gpt4free resource-registry boundary: runtime_eligible stays false).
"""
import argparse, json, sys, urllib.request
from pathlib import Path

REPO = "timerloggedout-spec/g4f-working_fork"
RAW = "https://raw.githubusercontent.com/" + REPO + "/{ref}/{path}"

def fetch(ref, path):
    with urllib.request.urlopen(RAW.format(ref=ref, path=path), timeout=60) as r:
        return r.read()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main", help="source ref (branch or commit SHA)")
    ap.add_argument("--source-sha", default=None, help="resolved source commit SHA to record")
    ap.add_argument("--output", default="data/g4f-working/providers.json")
    args = ap.parse_args()

    pm = json.loads(fetch(args.ref, "provider/providers_models.json"))
    working_lines = fetch(args.ref, "working/working_results.txt").decode().strip().splitlines()
    summary = json.loads(fetch(args.ref, "working/test_results.json"))["summary"]

    working = {}
    for line in working_lines:
        parts = line.split("|")
        if len(parts) == 3:
            working.setdefault(parts[0], []).append({"model": parts[1], "type": parts[2]})

    providers = []
    for pid in sorted(pm):
        entry = pm[pid]
        info = entry.get("provider_info") or {}
        models = entry.get("models") or []
        providers.append({
            "id": pid,
            "label": info.get("label"),
            "url": info.get("url"),
            "auth": "none (per source list)",
            "runtime_eligible": False,
            "evidence_class": "REFERENCE_ONLY",
            "model_count": entry.get("model_count", len(models)),
            "models": models,
            "working_models": working.get(pid, []),
        })

    catalog = {
        "schema_version": "g4f-working-catalog-v1",
        "source": {
            "repo": REPO,
            "url": "https://github.com/" + REPO,
            "upstream": "https://github.com/xtekky/gpt4free",
            "ref": args.ref,
            "source_sha": args.source_sha,
            "lists": ["provider/providers_models.json", "provider/providers_models.txt",
                      "provider/models_for_testing.txt", "working/working_results.txt",
                      "working/test_results.json"],
            "policy": "Harvested list data only; entries are discovery references, not verified entitlements, and never authorize fetching or execution.",
        },
        "summary": {
            "providers": len(providers),
            "models_catalogued": sum(p["model_count"] for p in providers),
            "tester_summary": summary,
            "working_entries": sum(len(p["working_models"]) for p in providers),
            "providers_with_working_models": sum(1 for p in providers if p["working_models"]),
        },
        "providers": providers,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(catalog, indent=1, sort_keys=False) + "\n")
    print(json.dumps(catalog["summary"], indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
