"""nc-1 shared feature extraction — deterministic, stdlib only.
SIGNAL token: carries notation/ids/refs/numbers/code (information-bearing
per #320 + density scope: signal ÷ tokens). PROSE token: plain natural-
language word carrying none of those. prose_ratio = prose/total."""
import re
SYMBOLS = set("∧∨¬⇒→∘≫↦∈⊆∅✓⛔≥≤×Δλ≠⇒·—–|")
SHA = re.compile(r"^[0-9a-f]{7,40}$")
def classify_token(raw: str) -> str:
    t = raw.strip("*_`#>-•\"'()[]{}")
    if not t: return "other"
    if any(ch in SYMBOLS for ch in raw): return "signal"
    if any(ch.isdigit() for ch in t): return "signal"
    if SHA.match(t.lower()): return "signal"
    if "://" in t or t.startswith("@") or t.startswith("#"): return "signal"
    if any(c in t for c in "/_=+\\") and any(c.isalnum() for c in t): return "signal"
    if len(t) >= 2 and t.isupper() and t.isalpha(): return "signal"
    if t.replace("'", "").replace("-", "").isalpha(): return "prose"
    if any(c.isalpha() for c in t) and not any(c.isdigit() for c in t):
        return "prose" if sum(c.isalpha() for c in t) >= max(2, len(t) - 2) else "other"
    return "other"
def features(text: str) -> dict:
    toks = text.split()
    kinds = [classify_token(t) for t in toks]
    n = len(toks) or 1
    prose = kinds.count("prose"); signal = kinds.count("signal")
    return {"tokens": len(toks), "prose_tokens": prose, "signal_tokens": signal,
            "prose_ratio": round(prose / n, 4), "density": round(signal / n, 4),
            "symbol_density": round(signal / n, 4),
            "outcome_id_present": bool(re.search(r"#\d{3,}|\b[0-9a-f]{10}\b|PR #\d+", text)),
            "evidence_ref_present": bool(re.search(r"\b[0-9a-f]{10}\b|#\d{3,}|run \d{9,}|\b\d{10}\b", text))}
