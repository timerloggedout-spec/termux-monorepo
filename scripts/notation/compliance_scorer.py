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
    # Information-density effectiveness (nc-1 amendment, PR #2866):
    # signal items carried per token, where signal items = evidence
    # refs + notation glyphs (compressed connectives). prose_ratio
    # (score/verdict above) is diagnostic only under the amendment.
    density = round((f["sym_per_100w"] + f["ev_per_100w"]) / 100.0, 4)
    return {**f, "score": total, "verdict": verdict, "density": density}


# ---------------------------------------------------------------- v2 --
# Wave-2 features (nc-1 build order, Linguist canonical defs
# c.6552176904): (1) claim<->ref adjacency — signal counts ONLY refs
# adjacent to a claim (same clause/sentence, or the immediately
# following sentence); (2) symbol-function — a registry symbol counts
# as connective only with operands on both sides in the same clause.
# The operator set is DERIVED at runtime from linguist-panel-feed/v1
# (families with kind_detail == "symbol-map"); it is never hard-coded.
# v1 scoring above stays untouched: detectors compare as-built.

CLAIM_WORDS = {
    "merged", "landed", "verified", "verification", "complete",
    "completed", "closed", "closing", "pass", "passed", "fail",
    "failed", "failure", "success", "verdict", "decided", "decision",
    "ruled", "ruling", "approved", "rejected", "confirmed", "blocked",
    "delivered", "recorded", "filed", "dispatched", "outcome",
    "result", "results", "count", "counts", "total", "status",
    "state", "drift", "compliant", "borderline", "score", "scores",
    "selected", "escalated", "halted", "agreed", "accepted",
    "reproduced", "exact", "matched", "missing",
}
QUANTITY = re.compile(r"\b\d[\d,.]*\b")
STATE_TOKEN = re.compile(r"\b(CANDIDATE|EXTRACT|SUPERSEDE|NEED_EVIDENCE)\b")
FILE_LINE = re.compile(r"\b[\w./-]+\.\w+:\d+\b")
SENT_SPAN = re.compile(r"[^.!?\n]+[.!?]*\s*|\n+")
CLAUSE_SPLIT = re.compile(r"[.!?\n;,·]+")


def load_operator_set(feed_path: str) -> set:
    """Derive the registry operator set from a linguist-panel-feed/v1
    JSON file: variant tokens of symbol-map families that carry no
    alphanumeric/space characters."""
    import ast as _ast
    with open(feed_path) as fh:
        feed = json.load(fh)
    fams = {f["id"]: f for f in feed.get("families", [])}
    ops = set()
    for e in feed.get("entries", []):
        if fams.get(e.get("family_id"), {}).get("kind_detail") != "symbol-map":
            continue
        for key in ("variants", "match_variants"):
            v = e.get(key)
            if isinstance(v, str):
                try:
                    v = _ast.literal_eval(v)
                except Exception:
                    v = [v]
            if isinstance(v, list):
                for t in v:
                    if isinstance(t, str) and t and not re.search(r"[A-Za-z0-9 ]", t):
                        ops.add(t)
    return ops


def _sentences(text: str) -> list[str]:
    return [m.group(0) for m in SENT_SPAN.finditer(text) if m.group(0).strip()]


def _is_claim(sent: str) -> bool:
    # Refs are stripped first: a bare ref number is not a quantity
    # claim (otherwise every ref self-certifies its own adjacency).
    bare = sent
    for p in REF_PATTERNS:
        bare = p.sub(" ", bare)
    bare = FILE_LINE.sub(" ", bare)
    words = {w.lower() for w in WORD.findall(bare)}
    return bool(words & CLAIM_WORDS) or bool(QUANTITY.search(bare)) \
        or bool(STATE_TOKEN.search(bare))


def _refs_in(sent: str) -> int:
    n = sum(len(p.findall(sent)) for p in REF_PATTERNS)
    return n + len(FILE_LINE.findall(sent))


def adjacency(text: str) -> dict:
    """Refs adjacent to claims: refs inside a claim sentence, plus
    refs in the sentence immediately following a claim sentence."""
    sents = _sentences(text)
    total_refs = sum(_refs_in(s) for s in sents)
    adj = 0
    prev_claim = False
    for s in sents:
        claim = _is_claim(s)
        if claim or prev_claim:
            adj += _refs_in(s)
        prev_claim = claim
    words = max(len(WORD.findall(text)), 1)
    return {"refs_total": total_refs, "adj_refs": adj,
            "adj_ev_per_100w": round(100.0 * adj / words, 2)}


def connective_symbols(text: str, ops: set) -> dict:
    """Count registry-symbol occurrences that function as connectives
    (operand material on both sides within the same clause)."""
    if not ops:
        return {"sym_total": 0, "connective_sym": 0, "sym_function_ratio": 0.0,
                "connective_per_100w": 0.0}
    pat = re.compile("|".join(re.escape(o) for o in sorted(ops, key=len, reverse=True)))
    total = 0
    conn = 0
    for clause in CLAUSE_SPLIT.split(text):
        for m in pat.finditer(clause):
            total += 1
            left = clause[:m.start()].rstrip()
            right = clause[m.end():].lstrip()
            # Operands must be IMMEDIATELY adjacent: another operator
            # on either side means this occurrence is listed, not used.
            if left and right and re.search(r"[A-Za-z0-9)\]}]$", left) \
                    and re.search(r"^[A-Za-z0-9(\[{]", right):
                conn += 1
    words = max(len(WORD.findall(text)), 1)
    return {"sym_total": total, "connective_sym": conn,
            "sym_function_ratio": round(conn / total, 3) if total else 0.0,
            "connective_per_100w": round(100.0 * conn / words, 2)}


def score_v2(text: str, ops: set) -> dict:
    """v2 composite: v1 shape, but the evidence term counts ONLY
    claim-adjacent refs and the symbol term counts ONLY connective
    registry symbols. Thresholds unchanged (0.55 / 0.40)."""
    f = features(text)
    a = adjacency(text)
    c = connective_symbols(text, ops)
    s_sym = min(c["connective_per_100w"] / 6.0, 1.0)
    s_ev = min(a["adj_ev_per_100w"] / 3.0, 1.0)
    s_glue = 1.0 - min(f["glue_per_sent"] / 4.0, 1.0)
    s_len = 1.0 - min(f["mean_sent_words"] / 28.0, 1.0)
    # Signal-dominant weights: under the v1 weights the glue/length
    # terms (0.40 combined) swamp the now-sparser signal terms and
    # short drift fragments score compliant (observed R=0.04 on the
    # gold corpus). The 0.55/0.40 thresholds are unchanged.
    total = round(0.45 * s_sym + 0.35 * s_ev + 0.10 * s_glue + 0.10 * s_len, 3)
    verdict = "compliant" if total >= 0.55 else "borderline" if total >= 0.40 else "prose"
    return {**f, **a, **c, "score_v2": total, "verdict_v2": verdict,
            "density_v2": round((c["connective_per_100w"] + a["adj_ev_per_100w"]) / 100.0, 4)}


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
