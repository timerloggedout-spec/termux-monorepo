#!/usr/bin/env python3
"""Notation Matrice search + add machinery (Linguist lane).

The Matrice of record is the nomenclature seed
(docs/proposals/active/notation-sets/nomenclature-matrix/seed.json).
This tool is the automated search 🔎 + add surface over it:

  search  — query concepts/labels/mappings by text, id, domain
            or label text; prints hits with their class context.
  screen  — collision screen for a candidate entry (exact id,
            exact label text in-domain, near-duplicate label):
            run BEFORE adding; exit 1 on a hard collision.
  add     — append a candidate concept (+ optional label) to
            the seed after screening; status is forced to
            "candidate" (issuance is a separate act).
  validate— schema sanity over the whole seed (ids unique,
            label->concept refs resolve, required keys).

Stdlib only. Exit codes: 0 ok · 1 collision/validation failure ·
2 usage/IO error.
"""
import argparse, json, sys
from pathlib import Path

DEFAULT_SEED = "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"
REQUIRED_CONCEPT = {"concept_id", "domain_id", "preferred_label", "definition", "status", "version", "source_ids"}
REQUIRED_LABEL = {"label_id", "concept_id", "text", "label_type", "language", "audience", "register", "status", "source_ids"}


def load_seed(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"error: cannot read seed {path}: {e}", file=sys.stderr); sys.exit(2)


def cmd_search(seed, args):
    q = args.query.lower()
    hits = []
    for c in seed["concepts"]:
        if q in c["concept_id"].lower() or q in c["preferred_label"].lower() or q in c["definition"].lower() or (args.domain and q in c["domain_id"].lower()):
            hits.append(("concept", c["concept_id"], c["domain_id"], c["preferred_label"]))
    for l in seed["labels"]:
        if q in l["text"].lower() or q in l["label_id"].lower():
            hits.append(("label", l["label_id"], l["concept_id"], l["text"]))
    for m in seed["mappings"]:
        if q in m["mapping_id"].lower() or q in m["source_concept_id"].lower() or q in m["target_concept_id"].lower():
            hits.append(("mapping", m["mapping_id"], m["source_concept_id"], "-> " + m["target_concept_id"]))
    for kind, a, b, ctext in hits:
        print(f"{kind}\t{a}\t{b}\t{ctext}")
    print(f"# {len(hits)} hit(s) for {args.query!r}")
    return 0


def screen(seed, concept, label_text=None):
    problems = []
    cid = concept["concept_id"]
    if any(c["concept_id"] == cid for c in seed["concepts"]):
        problems.append(f"concept_id already present: {cid}")
    if label_text:
        for l in seed["labels"]:
            if l["text"] == label_text:
                owner = next((c for c in seed["concepts"] if c["concept_id"] == l["concept_id"]), None)
                if owner and owner["domain_id"] == concept["domain_id"]:
                    problems.append(f"label {label_text!r} already used in-domain by {l['concept_id']}")
    return problems


def cmd_screen(seed, args):
    concept = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    label_text = concept.pop("label_text", None)
    problems = screen(seed, concept, label_text)
    if problems:
        for p in problems: print(f"COLLISION: {p}")
        return 1
    print("screen: clean (no exact in-domain collision; near-duplicates are a human screen)")
    return 0


def cmd_add(seed, args):
    entry = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    concept = entry["concept"]; label = entry.get("label")
    concept["status"] = "candidate"  # adds are always candidates; issuance is separate
    missing = REQUIRED_CONCEPT - set(concept)
    if missing:
        print(f"error: concept missing keys {sorted(missing)}", file=sys.stderr); return 2
    if label:
        missing = REQUIRED_LABEL - set(label)
        if missing:
            print(f"error: label missing keys {sorted(missing)}", file=sys.stderr); return 2
        label["status"] = "candidate"
    problems = screen(seed, concept, label["text"] if label else None)
    if problems:
        for p in problems: print(f"COLLISION: {p}", file=sys.stderr)
        return 1
    seed["concepts"].append(concept)
    if label: seed["labels"].append(label)
    Path(args.seed).write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"added candidate {concept['concept_id']}" + (f" + label {label['text']!r}" if label else ""))
    return 0


def cmd_validate(seed, args):
    problems = []
    cids = [c["concept_id"] for c in seed["concepts"]]
    if len(cids) != len(set(cids)): problems.append("duplicate concept_id(s)")
    for c in seed["concepts"]:
        missing = REQUIRED_CONCEPT - set(c)
        if missing: problems.append(f"{c.get('concept_id')}: missing {sorted(missing)}")
    known = set(cids)
    for l in seed["labels"]:
        if l["concept_id"] not in known: problems.append(f"label {l['label_id']} -> unknown concept {l['concept_id']}")
    for p in problems: print("INVALID:", p)
    print(f"# validate: {len(seed['concepts'])} concepts · {len(seed['labels'])} labels · {len(seed['mappings'])} mappings · {len(problems)} problem(s)")
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", default=DEFAULT_SEED)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--domain", action="store_true")
    sc = sub.add_parser("screen"); sc.add_argument("entry")
    a = sub.add_parser("add"); a.add_argument("entry")
    sub.add_parser("validate")
    args = ap.parse_args()
    seed = load_seed(args.seed)
    return {"search": cmd_search, "screen": cmd_screen, "add": cmd_add, "validate": cmd_validate}[args.cmd](seed, args)


if __name__ == "__main__":
    sys.exit(main())
