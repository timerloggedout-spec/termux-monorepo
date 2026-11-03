#!/usr/bin/env python3
"""Podium ingest — snapshot -> versioned dataset + changes + conflicts.

[MUSEai]@{role:{scraping-tools}}

Rules (owner requirement 2026-11-03):
  - normalize a podium-snapshot/v1 into entities keyed by stable keys;
  - dedupe identical observations by content hash;
  - EVERY row keeps its receipt {source_url, captured_at, collector};
  - conflicting values for the same (entity, field) are kept as
    conflicts, NEVER silently merged;
  - diff against the previous dataset version -> changes
    {added, removed, changed} per entity kind (change detection for
    repeat crawls of the live field).

Output dataset envelope: podium-dataset/v1 {version, generated_from,
entities{...}, conflicts[], changes{}}.
Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def content_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def entity_key(kind: str, *parts: str) -> str:
    return kind + ":" + ":".join(p.strip().lower() for p in parts if p)


EGM_MARKERS = ("EGM instance #2 TEST filing", "RFP-EGM2-")


def egm_stamped(row: dict) -> bool:
    """Owner ruling (MoneyBall plan): EGM instance-#2 test-stamped items
    never enter dataset-derived evidence. Sources are lablab pages, so
    this is a defensive guard for any future source widening."""
    blob = json.dumps(row, ensure_ascii=False)
    return any(m in blob for m in EGM_MARKERS)


def normalize(snapshot: dict) -> dict[str, dict]:
    """snapshot rows -> {entity_key: entity} (receipt stripped from the
    hashed content, kept on the entity)."""
    ents: dict[str, dict] = {}

    def put(kind: str, key: str, fields: dict, receipt: dict):
        e = ents.setdefault(key, {"key": key, "kind": kind, "fields": {}, "receipts": []})
        for f, v in fields.items():
            e["fields"].setdefault(f, []).append(v)  # all values kept
        if receipt and receipt not in e["receipts"]:
            e["receipts"].append(receipt)

    for ed in snapshot.get("editions", []):
        put("edition", entity_key("edition", ed["slug"]),
            {"title": ed.get("title"), "url": ed.get("url"),
             "dates_seen": ed.get("dates_seen")}, ed.get("receipt"))
    for t in snapshot.get("prize_tiers", []):
        put("placement_tier", entity_key("tier", t["slug"], t["place"]),
            {"amounts": t.get("amounts")}, t.get("receipt"))
    for j in snapshot.get("judges", []):
        put("judge", entity_key("judge", j["slug"], j["name"]),
            {"name": j.get("name"), "title": j.get("title"),
             "edition": j["slug"]}, j.get("receipt"))
    for p in snapshot.get("projects", []):
        put("project", entity_key("project", p["edition_slug"], p["team_slug"], p["project_slug"]),
            {"title": p.get("title"), "tagline": p.get("tagline"),
             "placement_feed": p.get("placement"),
             "edition": p["edition_slug"], "team": p["team_slug"],
             "url": p.get("url"), "tech_tags": p.get("tech_tags")}, p.get("receipt"))
    # judge persons: identity-stable across editions (exact normalized
    # name, v1) so repeat-judge detection (MoneyBall test 3) can run.
    persons: dict[str, dict] = {}
    for j in snapshot.get("judges", []):
        persons.setdefault(j["name"], {"editions": [], "titles": {}})
        persons[j["name"]]["editions"].append(j["slug"])
        persons[j["name"]]["titles"][j["slug"]] = j.get("title")
    for name, info in persons.items():
        put("judge_person", entity_key("judge-person", name),
            {"name": name, "editions": sorted(set(info["editions"])),
             "titles": info["titles"]},
            (snapshot.get("judges") or [{}])[0].get("receipt"))
    return ents


def resolve(ents: dict[str, dict]) -> tuple[dict, list]:
    """Collapse single-value fields; multi-value fields become conflicts."""
    out, conflicts = {}, []
    for key, e in ents.items():
        fields = {}
        for f, values in e["fields"].items():
            uniq = {canon(v): v for v in values}
            if len(uniq) == 1:
                fields[f] = values[0]
            else:
                fields[f] = values[0]  # display value = first seen
                conflicts.append({
                    "entity": key, "field": f,
                    "values": list(uniq.values()),
                    "receipts": e["receipts"],
                })
        out[key] = {**e, "fields": fields,
                    "content_hash": content_hash(fields)}
    return out, conflicts


def diff(prev: dict, cur: dict) -> dict:
    prev_e = (prev or {}).get("entities", {})
    added = sorted(set(cur) - set(prev_e))
    removed = sorted(set(prev_e) - set(cur))
    changed = sorted(
        k for k in set(cur) & set(prev_e)
        if cur[k]["content_hash"] != prev_e[k].get("content_hash")
    )
    return {"added": added, "removed": removed, "changed": changed,
            "counts": {"added": len(added), "removed": len(removed), "changed": len(changed)}}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Podium ingest")
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--previous", help="previous dataset JSON (for diff/conflicts vs history)")
    ap.add_argument("--version", required=True, help="dataset version, e.g. 2026-11-03.v1")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    snapshot = json.load(open(args.snapshot, encoding="utf-8"))
    for kind_rows in ("editions", "prize_tiers", "judges", "projects"):
        kept = [r for r in snapshot.get(kind_rows, []) if not egm_stamped(r)]
        dropped = len(snapshot.get(kind_rows, [])) - len(kept)
        if dropped:
            print(f"EGM guard: dropped {dropped} stamped rows from {kind_rows}",
                  file=sys.stderr)
        snapshot[kind_rows] = kept
    prev = None
    if args.previous:
        prev = json.load(open(args.previous, encoding="utf-8"))

    ents, conflicts = resolve(normalize(snapshot))
    # conflicts vs previous version: same entity+field, different value
    if prev:
        for key, e in ents.items():
            pe = prev.get("entities", {}).get(key)
            if not pe:
                continue
            for f, v in e["fields"].items():
                pv = pe["fields"].get(f)
                if pv is not None and canon(pv) != canon(v):
                    conflicts.append({
                        "entity": key, "field": f,
                        "values": [pv, v],
                        "receipts": e["receipts"],
                        "note": f"changed since {prev.get('version')}",
                    })
    changes = diff(prev, ents)
    # Feasibility stamps (MoneyBall plan C1/C3/C8): honest counts from
    # THIS dataset; field n awaits the gallery leg, comments the
    # comments surface - both recorded as null/0 with the reason in the
    # design doc, never silently.
    per_edition: dict[str, dict] = {}
    for e in ents.values():
        ed = e["fields"].get("edition") or (
            e["key"].split(":")[1] if e["kind"] in ("edition", "placement_tier") else None)
        if not ed:
            continue
        slot = per_edition.setdefault(ed, {"podium_n": 0, "field_n": None,
                                           "judge_comments": 0, "community_comments": 0})
        if e["kind"] == "project" and e["fields"].get("placement_feed"):
            slot["podium_n"] += 1
    repeat_judges = sum(
        1 for e in ents.values()
        if e["kind"] == "judge_person" and len(e["fields"].get("editions", [])) > 1)
    feasibility = {"per_edition": per_edition,
                   "repeat_judges_exact_name": repeat_judges,
                   "comments_surface": "NOT_ESTABLISHED (no public comments in server-rendered pages, recon 2026-11-03)"}
    dataset = {
        "envelope": "podium-dataset/v1",
        "version": args.version,
        "generated_from": {
            "snapshot_captured_at": snapshot.get("captured_at"),
            "collector": snapshot.get("collector"),
            "sources": snapshot.get("sources", []),
        },
        "entities": ents,
        "feasibility": feasibility,
        "conflicts": conflicts,
        "changes": changes,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"dataset {args.version}: entities={len(ents)} conflicts={len(conflicts)} "
          f"changes={changes['counts']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
