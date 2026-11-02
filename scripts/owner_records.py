#!/usr/bin/env python3
"""Owner-records store tooling (owner decisions D1-D5, confirmed 2026-11-01).

Store: ops/owner-records/index.json - a plaintext ENVELOPE (L1 metadata
only: id, class, title, state, holder, source pointer). Record bodies are
age ciphertext files under ops/owner-records/bodies/, encrypted to the
per-class recipient whose public half lives in ops/owner-records/keys/.
Private key halves are NEVER in the repo: Secure Vault entry
OWNER_RECORDS_AGE_KEYS + the owner's offline backup.

Subcommands:
  seed     parse the two public registers (GATES-REGISTER.md,
           OWNER-REQUESTS.md) into the envelope. Deterministic.
  validate check an envelope against the L1 rules.
  xml      build owner-records.xml (envelope + ciphertext inline) from
           the envelope and the bodies dir. Vercel-only surface (D5):
           the XML is staged into the gated project's deploy tree, it is
           not committed to the dashboard app tree.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA = "owner-records/v1"
CLASSES = ["authorizations", "gates", "clearances", "bets", "decisions"]
KEY_CLASSES = ["gates", "decisions", "authorizations", "clearances"]
BODY_FIELDS_FORBIDDEN = {"gate", "whats_needed", "resolution", "body",
                         "text", "note", "description"}
GATES_PATH = "docs/ops/GATES-REGISTER.md"
REQUESTS_PATH = "docs/ops/OWNER-REQUESTS.md"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def table_rows(lines):
    """Yield (section, cells) for markdown table data rows."""
    section = None
    for line in lines:
        if line.startswith("## "):
            section = line[3:].split("‖")[0].strip()
            continue
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] in ("item", "#"):
            continue
        if section and cells and any(cells):
            yield section, cells


def seed(root, generated_at):
    gates_text = (root / GATES_PATH).read_text().splitlines()
    req_text = (root / REQUESTS_PATH).read_text().splitlines()
    gates, per_section = [], {}
    for section, cells in table_rows(gates_text):
        if len(cells) < 4:
            continue
        item, holder, state = cells[0], cells[-1], cells[-2]
        per_section[section] = per_section.get(section, 0) + 1
        gates.append({
            "id": "gate-%s-%02d" % (slug(section), per_section[section]),
            "class": "gates", "title": item, "state": state,
            "holder": holder,
            "source": {"path": GATES_PATH, "section": section},
            "key_class": "gates", "body_status": "pending-keys",
            "body_file": None})
    decisions = []
    for section, cells in table_rows(req_text):
        if section == "OPEN" and len(cells) >= 6 and cells[0].isdigit():
            decisions.append({
                "id": "decision-open-%s" % cells[0], "class": "decisions",
                "title": cells[1], "state": "OPEN", "holder": cells[2],
                "since": cells[4],
                "source": {"path": REQUESTS_PATH, "section": "OPEN"},
                "key_class": "decisions", "body_status": "pending-keys",
                "body_file": None})
        elif section == "RESOLVED" and len(cells) >= 3:
            decisions.append({
                "id": "decision-%s" % slug(cells[0]), "class": "decisions",
                "title": cells[1], "state": "RESOLVED",
                "source": {"path": REQUESTS_PATH, "section": "RESOLVED"},
                "key_class": "decisions", "body_status": "pending-keys",
                "body_file": None})
    by_class = {
        "authorizations": {
            "class": "authorizations", "state": "not_established",
            "key_class": "authorizations",
            "note": "No authorizations register exists in the repo "
                    "(inventory PR #3505); docs/agentic/phase-approvals.json "
                    "is an empty stub, excluded.",
            "source_refs": [], "records": []},
        "gates": {
            "class": "gates", "state": "established",
            "key_class": "gates", "source_refs": [GATES_PATH],
            "records": gates},
        "clearances": {
            "class": "clearances", "state": "not_established",
            "key_class": "clearances",
            "note": "Class does not exist in the repo (inventory PR #3505).",
            "source_refs": [], "records": []},
        "bets": {
            "class": "bets", "state": "not_established",
            "key_class": None,
            "note": "BetLedgerEntry schema held at docs/proposals/active/"
                    "model-selection-market/schemas/bet-ledger.schema.json; "
                    "no ledger data in repo. No key class in v1 (owner "
                    "decision D-set keys x4); a key is minted per-record "
                    "if a body ever needs one.",
            "source_refs": ["docs/proposals/active/model-selection-market/"
                            "schemas/bet-ledger.schema.json"],
            "records": []},
        "decisions": {
            "class": "decisions", "state": "established",
            "key_class": "decisions", "source_refs": [REQUESTS_PATH],
            "records": decisions},
    }
    return {
        "schema": SCHEMA, "generated_at": generated_at,
        "seeded_from": {
            "inventory": "ops/tracking/owner-records-inventory.json",
            "registers": [GATES_PATH, REQUESTS_PATH]},
        "keys": {k: {"recipient": None, "status": "pending-owner-step"}
                 for k in KEY_CLASSES},
        "cautions": [
            "Envelope rows are L1 metadata only - never body text.",
            "Seed records derive from already-public registers; the "
            "public repo-tracking feed may join envelope rows only, "
            "never record bodies."],
        "classes": [by_class[c] for c in CLASSES]}


def validate(env):
    errs = []
    if env.get("schema") != SCHEMA:
        errs.append("schema != %s" % SCHEMA)
    seen = set()
    names = [c.get("class") for c in env.get("classes", [])]
    if names != CLASSES:
        errs.append("classes != %s (got %s)" % (CLASSES, names))
    for k, v in env.get("keys", {}).items():
        if k not in KEY_CLASSES:
            errs.append("unknown key class %s" % k)
        if v.get("status") == "active" and not v.get("recipient"):
            errs.append("key class %s active without recipient" % k)
    for cls in env.get("classes", []):
        if cls.get("key_class") not in KEY_CLASSES + [None]:
            errs.append("class %s key_class invalid" % cls.get("class"))
        for r in cls.get("records", []):
            if r["id"] in seen:
                errs.append("duplicate id %s" % r["id"])
            seen.add(r["id"])
            if r.get("class") != cls.get("class"):
                errs.append("record %s class mismatch" % r["id"])
            for f in BODY_FIELDS_FORBIDDEN:
                if f in r:
                    errs.append("record %s carries body field %s (L1 only)"
                                % (r["id"], f))
            if not r.get("title") or not r.get("state"):
                errs.append("record %s missing title/state" % r["id"])
            if not r.get("source", {}).get("path"):
                errs.append("record %s missing source.path" % r["id"])
            bs = r.get("body_status")
            if bs not in ("pending-keys", "encrypted", "none"):
                errs.append("record %s body_status %r" % (r["id"], bs))
            if bs == "encrypted" and not r.get("body_file"):
                errs.append("record %s encrypted without body_file"
                            % r["id"])
            if bs != "encrypted" and r.get("body_file"):
                errs.append("record %s body_file without encrypted status"
                            % r["id"])
    return errs


def build_xml(env, bodies_dir):
    root = ET.Element("owner-records", {
        "schema": env["schema"], "generated_at": env["generated_at"]})
    for cls in env["classes"]:
        cel = ET.SubElement(root, "class", {
            "name": cls["class"], "state": cls["state"],
            "key-class": cls.get("key_class") or ""})
        for r in cls["records"]:
            rel = ET.SubElement(cel, "record", {
                "id": r["id"], "state": r["state"],
                "body-status": r["body_status"]})
            ET.SubElement(rel, "title").text = r["title"]
            sattrs = {"path": r["source"]["path"]}
            if r["source"].get("section"):
                sattrs["section"] = r["source"]["section"]
            ET.SubElement(rel, "source", sattrs)
            bel = ET.SubElement(rel, "body")
            if r["body_status"] == "encrypted" and r.get("body_file"):
                bel.text = (bodies_dir / Path(r["body_file"]).name
                            ).read_text().strip()
            else:
                bel.set("status", r["body_status"])
    ET.indent(root)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            + ET.tostring(root, encoding="unicode") + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seed", "validate", "xml"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--index", default="ops/owner-records/index.json")
    ap.add_argument("--bodies", default="ops/owner-records/bodies")
    ap.add_argument("--generated-at", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    root = Path(a.root)
    if a.cmd == "seed":
        env = seed(root, a.generated_at)
        errs = validate(env)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        text = json.dumps(env, indent=1, ensure_ascii=False) + "\n"
    elif a.cmd == "validate":
        env = json.loads((root / a.index).read_text())
        errs = validate(env)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        print("envelope valid: %d classes, %d records" % (
            len(env["classes"]),
            sum(len(c["records"]) for c in env["classes"])))
        return 0
    else:
        env = json.loads((root / a.index).read_text())
        errs = validate(env)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        text = build_xml(env, root / a.bodies)
    if a.out:
        Path(a.out).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
