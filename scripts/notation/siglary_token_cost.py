#!/usr/bin/env python3
"""Siglary token-cost census: notation form vs plain-English expansion.

Measures BPE token cost of each register entry (GLYPHS, CHORDS, OPERATORS)
against its plain expansion, in mid-sentence context (leading space), under
public tokenizers. Additive evidence for SIGLARY-STANDARD.md §4 (Cost).

Source of tokenizers: openai/tiktoken (MIT) — https://github.com/openai/tiktoken
  o200k_base: GPT-4o / o-series family;  cl100k_base: GPT-4 / GPT-3.5 family.
Run: pip install tiktoken && python3 scripts/notation/siglary_token_cost.py
Writes: docs/proposals/active/notation-sets/data/siglary-token-cost.json
"""
from __future__ import annotations
import json, pathlib, sys
import tiktoken

ENCODINGS = ["o200k_base", "cl100k_base"]

# (form, plain expansion, class) — members of record per CAVEMAN-MICRO-DENSE-V2.md
ENTRIES = [
    # OPERATORS (class table, "Operators of record")
    ("∧", "and", "OPERATOR"), ("¬", "not", "OPERATOR"), ("∨", "or", "OPERATOR"),
    ("⇒", "implies", "OPERATOR"), ("∀", "for all", "OPERATOR"),
    ("∃", "there exists", "OPERATOR"), ("∅", "empty", "OPERATOR"),
    ("∈", "in", "OPERATOR"), ("∆", "change", "OPERATOR"),
    ("x++", "x stepped up once", "OPERATOR"), ("≅", "conforms to", "OPERATOR"),
    # GLYPHS (members of record)
    ("👁", "verified", "GLYPH"), ("🧐", "investigating", "GLYPH"),
    ("🧾", "receipt", "GLYPH"), ("❄", "frozen", "GLYPH"), ("⚖", "ruling", "GLYPH"),
    ("⛔", "blocked", "GLYPH"), ("👆", "owner action", "GLYPH"),
    ("⤴", "dispatch", "GLYPH"), ("🟢", "live", "GLYPH"), ("🔴", "down", "GLYPH"),
    ("🟡", "degraded", "GLYPH"),
    # CHORDS (Shorthand Domains)
    ("ent", "entry", "CHORD"), ("sub", "submission", "CHORD"), ("jdg", "judging", "CHORD"),
    ("ven", "venue", "CHORD"), ("qta", "quota", "CHORD"), ("tkn", "token", "CHORD"),
    ("wnd", "window", "CHORD"), ("brn", "burn", "CHORD"), ("bkt", "bucket", "CHORD"),
    ("attr", "attribution", "CHORD"), ("mrg", "merge", "CHORD"), ("brnch", "branch", "CHORD"),
    ("cmt", "commit", "CHORD"), ("gte", "gate", "CHORD"), ("chk", "check run", "CHORD"),
    ("wfl", "workflow", "CHORD"), ("rev", "review", "CHORD"), ("pl", "pool", "CHORD"),
    ("ldg", "ledger", "CHORD"), ("stl", "settlement", "CHORD"), ("prf", "proof", "CHORD"),
    ("stmt", "statement", "CHORD"), ("cyc", "cycle", "CHORD"), ("itr", "iteration", "CHORD"),
    ("pvd", "provider", "CHORD"), ("mdl", "model", "CHORD"), ("endp", "endpoint", "CHORD"),
    ("dpl", "deploy", "CHORD"), ("hst", "hosting", "CHORD"), ("snp", "snapshot", "CHORD"),
]

# Whole A2A stamp, three registers (same content)
STAMPS = {
    "chords_glyphs": "⤴ main→delphi · mrg wfl gte · 🧾 #1537 ∧ run 42262638671 · ∆ ask: ⛔ qta ¬ 🟢",
    "operators_words": "dispatch main→delphi · merge workflow gate · receipt #1537 ∧ run 42262638671 · ∆ ask: blocked quota ¬ live",
    "plain": "dispatch from main to delphi: merge workflow gate, receipt #1537 and run 42262638671, change asked: blocked, quota not live",
}

def n(enc, s: str) -> int:
    return len(enc.encode(" " + s))

def main() -> int:
    out = {"tokenizer_source": "https://github.com/openai/tiktoken",
           "tiktoken_version": getattr(tiktoken, "__version__", "unknown"),
           "context": "leading space (mid-sentence)", "encodings": {}}
    for name in ENCODINGS:
        enc = tiktoken.get_encoding(name)
        rows, by = [], {}
        for form, plain, cls in ENTRIES:
            f, p = n(enc, form), n(enc, plain)
            rows.append({"form": form, "plain": plain, "class": cls,
                         "form_tokens": f, "plain_tokens": p, "delta": f - p})
            b = by.setdefault(cls, {"n": 0, "form": 0, "plain": 0, "cheaper": 0, "tie": 0, "costlier": 0})
            b["n"] += 1; b["form"] += f; b["plain"] += p
            b["cheaper" if f < p else "tie" if f == p else "costlier"] += 1
        stamps = {k: {"chars": len(v), "tokens": len(enc.encode(v))} for k, v in STAMPS.items()}
        out["encodings"][name] = {"by_class": by, "stamps": stamps, "rows": rows}
    out["stamp_text"] = STAMPS
    dst = pathlib.Path(__file__).resolve().parents[2] / "docs/proposals/active/notation-sets/data/siglary-token-cost.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    for name, e in out["encodings"].items():
        print(name, json.dumps(e["by_class"], ensure_ascii=False), json.dumps(e["stamps"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
