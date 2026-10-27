#!/usr/bin/env python3
"""Linguist Panel feed collector (linguist-panel-feed/v1).

Builds the dashboard Linguist Admin Panel's data feed from the mapping
systems of record — and nothing else:

  - workspace/compression_sandbox/cedrlang/cedrlang.py
    (SYMBOL_MAP, MAPPINGS, STOPWORDS — imported, never transcribed)
  - workspace/compression_sandbox/cedrlang/phase_codec.py
    (LEET_MAP, CANONICAL_TOKENS, VARIANT_INDEX — imported)
  - workspace/compression_sandbox/cedrlang/cid.py
    (CedarIndex pointer hash, ALL_COMMANDS seed registry)
  - harmony_hub/config/grimoire/1337_D1CT10N4RY.md (markdown tables)
  - harmony_hub/config/GRIMOIRE_DICTIONARY.md (1337/Grimoire/Orchestra)
  - docs/proposals/active/notation-sets/nomenclature-matrix/seed.json
  - docs/schemas/routing-notation.yaml
  - archwiz/pointer_index.json (count-only; session data, not lexical)

Contract: docs/ops/LINGUIST-PANEL-FEED.md. Canonical registry: the
family table in that contract names one source of truth per family;
on conflict the runtime code wins over prose dictionaries.

Round-trip verification runs the actual codecs at collection time
(differential discipline, 2026-10-20 codec-revert lesson): an entry is
`round_trip_verified: true` only when the live code reproduces it.
Lossy-by-design entries (many-to-one symbols, stopword elision,
stochastic leet chars) report false/null with the reason in `note` —
never a silent semantics claim.

Stdlib only. Refresh pattern mirrors
scripts/delphi/oracle_panel_feed.py: the regenerated feed lands by
PR, never by direct commit.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "linguist-panel-feed/v1"

CEDRLANG_DIR = "workspace/compression_sandbox/cedrlang"
SOURCES = {
    "cedrlang": f"{CEDRLANG_DIR}/cedrlang.py",
    "phase_codec": f"{CEDRLANG_DIR}/phase_codec.py",
    "cid": f"{CEDRLANG_DIR}/cid.py",
    "grimoire_1337": "harmony_hub/config/grimoire/1337_D1CT10N4RY.md",
    "grimoire_dict": "harmony_hub/config/GRIMOIRE_DICTIONARY.md",
    "nomenclature_seed": "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json",
    "routing_notation": "docs/schemas/routing-notation.yaml",
    "archwiz_pointer_index": "archwiz/pointer_index.json",
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _anchor(lines: list[str], needle: str) -> int | None:
    """1-based line of the first line containing `needle` (span anchor)."""
    for i, line in enumerate(lines, 1):
        if needle in line:
            return i
    return None


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "x"


class Feed:
    def __init__(self, root: Path):
        self.root = root
        self.entries: list[dict] = []
        self.families: list[dict] = []
        self._lines: dict[str, list[str]] = {}

    def lines(self, rel: str) -> list[str]:
        if rel not in self._lines:
            self._lines[rel] = (self.root / rel).read_text(
                encoding="utf-8", errors="replace").splitlines()
        return self._lines[rel]

    def family(self, fid, name, kind, source, direction, canonical,
               entry_count, included=True, rt=None, note=None):
        fam = {
            "id": fid, "name": name, "kind": kind, "source_path": source,
            "direction": direction, "canonical_source": canonical,
            "entry_count": entry_count, "entries_included": included,
            "round_trip": rt or {"verified": 0, "failed": 0, "not_applicable": 0},
        }
        if note:
            fam["note"] = note
        self.families.append(fam)
        return fam

    def entry(self, family, source, variants, direction, prov_path,
              needle, rt_verified, note=None, extra=None):
        e = {
            "id": f"{family}:{_slug(source)}",
            "family": family,
            "source": source,
            "variants": variants,
            "direction": direction,
            "provenance": {
                "path": prov_path,
                "line": _anchor(self.lines(prov_path), needle),
            },
            "round_trip_verified": rt_verified,
        }
        if note:
            e["note"] = note
        if extra:
            e.update(extra)
        self.entries.append(e)
        return e

    def rt_counts(self, fid):
        es = [e for e in self.entries if e["family"] == fid]
        return {
            "verified": sum(1 for e in es if e["round_trip_verified"] is True),
            "failed": sum(1 for e in es if e["round_trip_verified"] is False),
            "not_applicable": sum(1 for e in es if e["round_trip_verified"] is None),
        }


def build(root: Path) -> dict:
    feed = Feed(root)
    cedr = _load_module("cedrlang", root / SOURCES["cedrlang"])
    phase = _load_module("phase_codec", root / SOURCES["phase_codec"])
    cid = _load_module("cid", root / SOURCES["cid"])

    # --- cedrlang-symbol: phrase <-> symbol (compress/expand) ----------
    # REV_MAP is last-wins per symbol, so duplicate-symbol phrases are
    # lossy on decode by construction; verify each entry against the
    # live pair (compress then expand) and report the truth per entry.
    fid = "cedrlang-symbol"
    for phrase, symbol in cedr.SYMBOL_MAP.items():
        enc = cedr.compress(f"x{phrase}y")
        dec = cedr.expand(f"x{symbol}y")
        ok = symbol.strip() in enc and dec == f"x{phrase}y"
        feed.entry(fid, phrase.strip(), [symbol.strip()], "bidirectional",
                   SOURCES["cedrlang"], f'"{phrase}"', ok,
                   note=None if ok else
                   "lossy decode: expand() of the symbol yields "
                   f"'{dec}' here (many-to-one symbol and/or symbol-pair "
                   "substring collision in REV_MAP)")
    feed.family(fid, "CedrLang symbol substitution", "symbol-map",
                SOURCES["cedrlang"], "bidirectional", SOURCES["cedrlang"],
                len(cedr.SYMBOL_MAP), rt=feed.rt_counts(fid))

    # --- cedrlang-compression: human <-> compressed token --------------
    # The word mappings live in the compile_doc/decompile_doc path,
    # not in compress()/expand(); verify on that path, case-insensitive
    # (apply_casing normalizes some tokens, e.g. 3ch0 -> Echo).
    fid = "cedrlang-compression"
    for human, comp in cedr.MAPPINGS:
        ok = (cedr.compile_doc(human).strip().lower() == comp.lower()
              and cedr.decompile_doc(comp).strip().lower() == human.lower())
        feed.entry(fid, human, [comp], "bidirectional",
                   SOURCES["cedrlang"], f'("{human}"', ok)
    feed.family(fid, "CedrLang compression mappings", "word-map",
                SOURCES["cedrlang"], "bidirectional", SOURCES["cedrlang"],
                len(cedr.MAPPINGS), rt=feed.rt_counts(fid))

    # --- cedrlang-stopwords: elision list (encode-only, lossy) ---------
    fid = "cedrlang-stopwords"
    for word in sorted(cedr.STOPWORDS):
        feed.entry(fid, word, [], "encode-only", SOURCES["cedrlang"],
                   f'"{word}"', False,
                   note="elided by compress()/caveman(); lossy by design")
    feed.family(fid, "CedrLang stopword elision", "elision-list",
                SOURCES["cedrlang"], "encode-only", SOURCES["cedrlang"],
                len(cedr.STOPWORDS), rt=feed.rt_counts(fid))

    # --- phase-codec-leet-chars ----------------------------------------
    fid = "phase-codec-leet-chars"
    for letter, digit in phase.LEET_MAP.items():
        feed.entry(fid, letter, [digit], "encode-only",
                   SOURCES["phase_codec"], f'"{letter}": "{digit}"', None,
                   note="char substitution is ambiguous alone (e.g. 4 = a); "
                        "reversibility exists only at canonical-token level")
    feed.family(fid, "Phase codec leet character map (PR #154, p=0.70)",
                "char-map", SOURCES["phase_codec"], "encode-only",
                SOURCES["phase_codec"], len(phase.LEET_MAP),
                rt=feed.rt_counts(fid))

    # --- phase-codec-canonical-tokens -----------------------------------
    fid = "phase-codec-canonical-tokens"
    variants_of = {}
    for var, canon in phase.VARIANT_INDEX.items():
        variants_of.setdefault(canon, []).append(var)
    for token in phase.CANONICAL_TOKENS:
        ok = (phase.from_1337speak(
            phase.to_1337speak(token, probability=1.0)).lower()
            == token.lower())
        feed.entry(fid, token, sorted(variants_of.get(token, [])),
                   "bidirectional", SOURCES["phase_codec"], f'"{token}"',
                   ok, note="round-trip case-insensitive: from_1337speak "
                            "may normalize casing (FAST_CASING table)")
    feed.family(fid, "Phase codec canonical tokens + leet variants",
                "token-variants", SOURCES["phase_codec"], "bidirectional",
                SOURCES["phase_codec"], len(phase.CANONICAL_TOKENS),
                rt=feed.rt_counts(fid),
                note=f"variant index: {len(phase.VARIANT_INDEX)} forms, "
                     f"{len(phase.NON_CANONICAL_INDEX)} non-canonical")

    # --- grimoire tables (prose dictionaries; code wins on conflict) ----
    grim_lines = feed.lines(SOURCES["grimoire_1337"])
    canon_by_comp = {c.lower(): h for h, c in cedr.MAPPINGS}

    fid = "grimoire-char-variants"
    section = None
    n = 0
    for line in grim_lines:
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"\| ([A-Z]) \| (.+) \|", line)
        if m and section and section.startswith("Character"):
            variants = [v.strip() for v in m.group(2).split(",")]
            feed.entry(fid, m.group(1), variants, "encode-only",
                       SOURCES["grimoire_1337"], f"| {m.group(1)} |", None,
                       note="prose dictionary; superset of phase-codec "
                            "LEET_MAP, not runtime authority")
            n += 1
    feed.family(fid, "Grimoire 1337 character variants (prose)",
                "char-map", SOURCES["grimoire_1337"], "encode-only",
                SOURCES["phase_codec"], n, rt=feed.rt_counts(fid),
                note="canonical runtime map is phase_codec.LEET_MAP")

    fid = "grimoire-core-castings"
    section = None
    n = 0
    for line in grim_lines:
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"\| ([^|]+) \| ([^|]+) \|$", line.strip())
        if m and section and section.startswith("Core Castings"):
            term, meaning = m.group(1).strip(), m.group(2).strip()
            if term.lower() in ("term",):
                continue
            feed.entry(fid, term, [meaning], "decode-only",
                       SOURCES["grimoire_1337"], f"| {term} |", None)
            n += 1
    feed.family(fid, "Grimoire core castings (1337 term -> meaning)",
                "glossary", SOURCES["grimoire_1337"], "decode-only",
                SOURCES["grimoire_1337"], n, rt=feed.rt_counts(fid))

    fid = "grimoire-protocol-terms"
    section = None
    n = 0
    for line in grim_lines:
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"\| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", line.strip())
        if m and section and section.startswith("Grimoire Protocol"):
            term, meaning, leet = (g.strip() for g in m.groups())
            if meaning.lower() == "meaning":
                continue
            ok = canon_by_comp.get(leet.lower()) == term.lower() or None
            feed.entry(fid, term, [leet], "bidirectional",
                       SOURCES["grimoire_1337"], term, ok,
                       extra={"meaning": meaning},
                       note=None if ok else
                       "leet variant not a cedrlang canonical token")
            n += 1
    feed.family(fid, "Grimoire protocol terms (term <-> leet variant)",
                "glossary", SOURCES["grimoire_1337"], "bidirectional",
                SOURCES["cedrlang"], n, rt=feed.rt_counts(fid))

    # --- grimoire-orchestra crosswalk ------------------------------------
    fid = "grimoire-orchestra-crosswalk"
    n = 0
    for line in feed.lines(SOURCES["grimoire_dict"]):
        m = re.match(r"\| `([^`]+)` \| `?([^|`]+)`? \| `?([^|`]+)`? \|", line)
        if m:
            leet, grimoire, orchestra = (g.strip() for g in m.groups())
            ok = canon_by_comp.get(leet.lower()) == grimoire.lower() or None
            feed.entry(fid, leet, [grimoire, orchestra], "bidirectional",
                       SOURCES["grimoire_dict"], f"| `{leet}`", ok,
                       extra={"grimoire": grimoire, "orchestra": orchestra},
                       note=None if ok is True else
                       "no matching cedrlang canonical pair")
            n += 1
    feed.family(fid, "Grimoire dictionary crosswalk (1337/Grimoire/Orchestra)",
                "crosswalk", SOURCES["grimoire_dict"], "bidirectional",
                SOURCES["cedrlang"], n, rt=feed.rt_counts(fid))

    # --- cedar-pointer-commands (cid.py seed registry) -------------------
    # Verify with the real CedarIndex against a throwaway index file:
    # register(cmd) -> pointer, expand(pointer) -> normalized command.
    fid = "cedar-pointer-commands"
    with tempfile.TemporaryDirectory() as tmp:
        cid.CedarIndex.INDEX_FILE = Path(tmp) / "cedar_index.json"
        index = cid.CedarIndex()
        for cmd in cid.ALL_COMMANDS:
            ptr = index.register(cmd)
            ok = index.expand(ptr) == index._norm(cmd)
            feed.entry(fid, cmd, [ptr], "bidirectional", SOURCES["cid"],
                       f'"{cmd}"', ok,
                       note="decode requires the runtime registry "
                            "(~/.cedar/cedar_index.json), not committed")
    feed.family(fid, "CedarIndex pointer seed commands (cid.py)",
                "hash-pointer", SOURCES["cid"], "bidirectional",
                SOURCES["cid"], len(cid.ALL_COMMANDS),
                rt=feed.rt_counts(fid),
                note="pointers are sha256/base36 4-char hashes prefixed →; "
                     "live registry is runtime-local, never in-repo")

    # --- nomenclature matrix (notation-sets seed) -------------------------
    seed = json.loads((root / SOURCES["nomenclature_seed"]).read_text())
    fid = "nomenclature-concepts"
    for c in seed["concepts"]:
        feed.entry(fid, c["preferred_label"], [c["concept_id"]],
                   "definitional", SOURCES["nomenclature_seed"],
                   f'"{c["concept_id"]}"', None,
                   extra={"concept_id": c["concept_id"],
                          "domain_id": c["domain_id"],
                          "status": c["status"]})
    feed.family(fid, "Nomenclature matrix concepts", "concept-registry",
                SOURCES["nomenclature_seed"], "definitional",
                SOURCES["nomenclature_seed"], len(seed["concepts"]),
                rt=feed.rt_counts(fid),
                note="candidate-status research data (SKOS-aligned); "
                     "not runtime authority")

    fid = "nomenclature-labels"
    for lab in seed["labels"]:
        feed.entry(fid, lab["text"], [lab["label_id"]], "definitional",
                   SOURCES["nomenclature_seed"], f'"{lab["label_id"]}"',
                   None, extra={"label_id": lab["label_id"],
                                "concept_id": lab["concept_id"],
                                "label_type": lab["label_type"],
                                "status": lab["status"]})
    feed.family(fid, "Nomenclature matrix labels", "label-registry",
                SOURCES["nomenclature_seed"], "definitional",
                SOURCES["nomenclature_seed"], len(seed["labels"]),
                rt=feed.rt_counts(fid))

    fid = "nomenclature-mappings"
    for mp in seed["mappings"]:
        feed.entry(fid, mp["source_concept_id"], [mp["target_concept_id"]],
                   "definitional", SOURCES["nomenclature_seed"],
                   f'"{mp["mapping_id"]}"', None,
                   extra={"mapping_id": mp["mapping_id"],
                          "relation": mp["relation"],
                          "confidence": mp["confidence"],
                          "status": mp["status"]})
    feed.family(fid, "Nomenclature matrix concept mappings (SKOS relations)",
                "concept-map", SOURCES["nomenclature_seed"], "definitional",
                SOURCES["nomenclature_seed"], len(seed["mappings"]),
                rt=feed.rt_counts(fid))

    # --- routing notation (definitional vocabulary) -----------------------
    fid = "routing-notation"
    section = None
    n = 0
    for line in feed.lines(SOURCES["routing_notation"]):
        m = re.match(r"^  (\w[\w-]*):", line)
        if m:
            section = m.group(1)
            continue
        m = re.match(r"^    ([\w-]+):\s*(?:\"([^\"]*)\"|(.*))?$", line)
        if m and section in ("topology", "operators", "evidence",
                             "experiment_axes"):
            definition = m.group(2) if m.group(2) is not None else (m.group(3) or "")
            term = m.group(1)
            feed.entry(fid, term, [], "definitional",
                       SOURCES["routing_notation"], f"{term}:", None,
                       extra={"section": section, "definition": definition})
            n += 1
    feed.family(fid, "Routing notation vocabulary", "vocabulary",
                SOURCES["routing_notation"], "definitional",
                SOURCES["routing_notation"], n, rt=feed.rt_counts(fid))

    # --- archwiz pointer index (count-only) --------------------------------
    pidx = json.loads((root / SOURCES["archwiz_pointer_index"]).read_text())
    fid = "archwiz-pointer-index"
    feed.family(fid, "ArchWiz pointer index (hash -> session/manifest)",
                "hash-pointer", SOURCES["archwiz_pointer_index"],
                "decode-only", SOURCES["archwiz_pointer_index"],
                len(pidx), included=False,
                note="entries are session/manifest data, not lexical "
                     "mappings; counted, not enumerated in the feed")

    counts = {f["id"]: f["entry_count"] for f in feed.families}
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/linguist/linguist_panel_feed.py",
        "contract": "docs/ops/LINGUIST-PANEL-FEED.md",
        "sources": SOURCES,
        "counts": {
            "families": len(feed.families),
            "entries_total": sum(counts.values()),
            "entries_included": len(feed.entries),
            "per_family": counts,
        },
        "families": feed.families,
        "entries": feed.entries,
        "gaps": [
            {"id": "mapping-pointer-index-missing",
             "detail": "archwiz/mapping_pointer_index.py is cited as the "
                       "mapping-pointer-index/v1 contract by "
                       "docs/linguist/ACTIONS-MAPPING-RECOVERY.md, "
                       "docs/proposals/active/notation-sets/"
                       "NSE-020-MAPPING-POINTER-ROUNDTRIP.md, "
                       "ROUNDTRIP-IMPLEMENTATION.md and "
                       "scripts/linguist/index_alignment.py, but the file "
                       "does not exist on master. NOT ESTABLISHED as "
                       "implemented."},
            {"id": "rev-grimoire-map-missing",
             "detail": "REV_GRIMOIRE_MAP / REV_SYMBOL_MAP are named in "
                       "ACTIONS-MAPPING-RECOVERY.md as historical reverse "
                       "tables; on master only REV_MAP (derived from "
                       "SYMBOL_MAP) exists in cedrlang.py."},
            {"id": "linguist-machine-parity-placeholder",
             "detail": "docs/proposals/active/linguist-machine-parity/ "
                       "holds LMP-01 as a posted placeholder only: zero "
                       "mapping entries, implementation not authorized "
                       "there. No family emitted."},
            {"id": "cedar-live-registry-not-in-repo",
             "detail": "CedarIndex live registrations live in "
                       "~/.cedar/cedar_index.json (runtime-local). The "
                       "feed carries only the 45 seed commands from "
                       "cid.py ALL_COMMANDS."},
            {"id": "encrypted-pointer-store-proposed",
             "detail": "PR #154's encrypted private mapping-pointer "
                       "store and Actions obfuscation hooks are proposed "
                       "in ACTIONS-MAPPING-RECOVERY.md, not verified as "
                       "deployed. No family emitted."},
        ],
        "excluded": [
            "harmony_hub/config/prompts/profiles/1337.json — prompt "
            "profile that *uses* leet surface, defines no mappings",
            "archwiz/vision_1337.py — prose/vision text, no mappings",
            "docs/proposals/active/notation-sets/ NSE-001..NSE-023 — "
            "proposal items governing the families above, not mapping "
            "entries themselves",
            ".deepcli/session_store/* — session artifacts, not mappings",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    data = build(Path(args.root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"{SCHEMA}: {data['counts']['families']} families, "
          f"{data['counts']['entries_included']} entries included, "
          f"{data['counts']['entries_total']} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
