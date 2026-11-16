"""nc-1 shared feature extraction — deterministic, stdlib only.
SIGNAL token: carries notation/ids/refs/numbers/code (information-bearing
per #320 + density scope: signal ÷ tokens). PROSE token: plain natural-
language word carrying none of those. prose_ratio = prose/total."""
import json
import re
SYMBOLS = set("∧∨¬⇒→∘≫↦∈⊆∅✓⛔≥≤×Δλ≠⇒·—–|")
SHA = re.compile(r"^[0-9a-f]{7,40}$")
def classify_token(raw: str) -> str:
    t = raw.strip("*_`#>-•\"'()[]{}")
    if not t: return "other"
    if '":' in raw or '":' in t: return "signal"  # JSON field key carries structure
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
ABSENT = {"not-established", "not_established", "not", "established",
          "null", "none", "unknown", "n/a", ""}

def _leaves(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from _leaves(v)
    elif isinstance(node, list):
        for v in node:
            yield from _leaves(v)
    else:
        yield node

def _leaf_signal(v) -> float:
    """Signal carried by one record leaf value (amended DESIGN: ids,
    decisions, quantities, evidence refs, novel facts; absent-state
    markers carry none)."""
    if isinstance(v, bool):
        return 0.5
    if isinstance(v, (int, float)):
        return 1.0
    if isinstance(v, str):
        t = v.strip().lower()
        if t in ABSENT or t.replace("-", "_") in ABSENT:
            return 0.0
        if any(c.isdigit() for c in t) or "#" in t or "sha" in t:
            return 1.0
        return 0.25  # a stated value (name/state) carries some signal
    return 0.0

def records_density(text: str):
    """Element-level density for machine records: signal_units over
    total leaf elements. Token density is meaningless on JSON — keys
    and absent-state values inflate it (corpus v2 build finding)."""
    try:
        doc = json.loads(text)
    except Exception:
        return None
    leaves = list(_leaves(doc))
    if not leaves:
        return 0.0
    return round(sum(_leaf_signal(v) for v in leaves) / len(leaves), 4)

def features(text: str, surface: str = "") -> dict:
    toks = text.split()
    kinds = [classify_token(t) for t in toks]
    n = len(toks) or 1
    prose = kinds.count("prose"); signal = kinds.count("signal")
    density = round(signal / n, 4)
    if surface == "records":
        rd = records_density(text)
        if rd is not None:
            density = rd
    return {"tokens": len(toks), "prose_tokens": prose, "signal_tokens": signal,
            "prose_ratio": round(prose / n, 4), "density": density,
            "symbol_density": round(signal / n, 4),
            "outcome_id_present": bool(re.search(r"#\d{3,}|\b[0-9a-f]{10}\b|PR #\d+", text)),
            "evidence_ref_present": bool(re.search(r"\b[0-9a-f]{10}\b|#\d{3,}|run \d{9,}|\b\d{10}\b", text))}
