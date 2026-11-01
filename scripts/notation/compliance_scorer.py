#!/usr/bin/env python3
"""Notation-compliance scorer — heuristic v1 (owner TEST, 2026-10-31).

Scores a text against the fleet notation spec (issue #320 Notation Sets
+ #1734 claim-level evidence provenance, as adopted in CLAUDE.md):
symbol-dense cadence, few prose connectives, short sentences, and a
claim-level evidence ref density.

Features (all length-normalized):
  sym_per_100w    notation glyphs + cadence tokens per 100 words
  glue_per_sent   prose connective/discourse words per sentence
  mean_sent_words mean words per sentence
  ev_per_100w     evidence refs (PR/issue numbers, hex SHAs, run ids,
                  URLs, repo paths, [MUSEai] markers) per 100 words

Composite score in [0, 1]; verdicts: >= 0.55 compliant,
0.40..0.55 borderline, < 0.40 prose. Report-only instrument: it
measures drift, it never gates anything by itself.

CLI: compliance_scorer.py FILE... | --text "..." | - (stdin)
     --json for machine output.
"""
from __future__ import annotations

import json
import re
import sys

GLYPHS = set("⊃→×✓∅Δ≈≥∴∘⇒≫↦∈⊆∧∨¬∵λ≠≤←↑↓↔⇔⊆⊂∀∃∞±·")
CADENCE_TOKENS = ("&&", "->", "=>", "::", ">>", ":=", "==")
GLUE = {
    "however", "therefore", "because", "moreover", "furthermore",
    "nevertheless", "consequently", "meanwhile", "although", "whereas",
    "thus", "hence", "accordingly", "additionally", "specifically",
    "particularly", "essentially", "generally", "typically", "ultimately",
    "overall", "indeed", "instead", "otherwise", "besides", "anyway",
    "actually", "basically", "importantly", "notably", "clearly",
}
REF_PATTERNS = (
    re.compile(r"#\d{2,}"),                       # PR / issue numbers
    re.compile(r"\b[0-9a-f]{7,40}\b"),            # hex SHAs / blob ids
    re.compile(r"\b\d{9,}\b"),                    # Actions run ids
    re.compile(r"https?://\S+"),                  # URLs
    re.compile(r"\[MUSEai\]"),                   # attribution markers
    re.compile(r"\b[\w./-]+\.(?:py|md|json|jsonl|yml|yaml|html|toml)\b"),  # paths
    re.compile(r"\bcomment \d{6,}\b"),            # comment ids
)
SENT_SPLIT = re.compile(r"[.!?]+\s+|\n+")
WORD = re.compile(r"[A-Za-z0-9_']+")


def features(text: str) -> dict:
    words = WORD.findall(text)
    n_words = max(len(words), 1)
    sentences = [s for s in SENT_SPLIT.split(text) if s.strip()]
    n_sent = max(len(sentences), 1)
    glyphs = sum(1 for ch in text if ch in GLYPHS)
    glyphs += sum(text.count(tok) for tok in CADENCE_TOKENS)
    lower = [w.lower() for w in words]
    glue = sum(1 for w in lower if w in GLUE)
    refs = sum(len(p.findall(text)) for p in REF_PATTERNS)
    return {
        "words": len(words),
        "sentences": len(sentences),
        "sym_per_100w": round(100.0 * glyphs / n_words, 2),
        "glue_per_sent": round(glue / n_sent, 2),
        "mean_sent_words": round(len(words) / n_sent, 1),
        "ev_per_100w": round(100.0 * refs / n_words, 2),
    }


def score(text: str) -> dict:
    f = features(text)
    s_sym = min(f["sym_per_100w"] / 6.0, 1.0)
    s_ev = min(f["ev_per_100w"] / 3.0, 1.0)
    s_glue = 1.0 - min(f["glue_per_sent"] / 4.0, 1.0)
    s_len = 1.0 - min(f["mean_sent_words"] / 28.0, 1.0)
    total = round(0.35 * s_sym + 0.25 * s_ev + 0.20 * s_glue + 0.20 * s_len, 3)
    verdict = "compliant" if total >= 0.55 else "borderline" if total >= 0.40 else "prose"
    return {**f, "score": total, "verdict": verdict}


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    texts: list[tuple[str, str]] = []
    if args and args[0] == "--text":
        texts.append(("--text", args[1]))
    elif args and args[0] == "-":
        texts.append(("<stdin>", sys.stdin.read()))
    else:
        for path in args:
            with open(path) as fh:
                texts.append((path, fh.read()))
    out = []
    for name, text in texts:
        r = score(text)
        out.append({"source": name, **r})
        if not as_json:
            print(f"{name}: score={r['score']} verdict={r['verdict']} "
                  f"sym/100w={r['sym_per_100w']} glue/sent={r['glue_per_sent']} "
                  f"sent_words={r['mean_sent_words']} ev/100w={r['ev_per_100w']}")
    if as_json:
        print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
