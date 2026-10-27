"""Tests for the Linguist Panel feed collector.

Includes the differential guard from the 2026-10-20 codec-revert
lesson: the feed's extracted mappings must equal the live module
constants exactly, and codec round-trips are re-run here against the
base implementations — a collector (or codec) change that silently
alters semantics fails these tests.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace" / "compression_sandbox" / "cedrlang"))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


collector = _load("linguist_panel_feed",
                  "scripts/linguist/linguist_panel_feed.py")
cedr = _load("cedrlang", "workspace/compression_sandbox/cedrlang/cedrlang.py")
phase = _load("phase_codec",
              "workspace/compression_sandbox/cedrlang/phase_codec.py")


def _feed():
    return collector.build(ROOT)


def test_schema_and_counts_consistent():
    feed = _feed()
    assert feed["schema"] == "linguist-panel-feed/v1"
    per = feed["counts"]["per_family"]
    assert feed["counts"]["families"] == len(feed["families"]) == len(per)
    assert feed["counts"]["entries_total"] == sum(per.values())
    included = sum(f["entry_count"] for f in feed["families"]
                   if f["entries_included"])
    assert feed["counts"]["entries_included"] == included == len(feed["entries"])
    for fam in feed["families"]:
        assert per[fam["id"]] == fam["entry_count"]


def test_differential_extraction_matches_live_modules():
    feed = _feed()
    by_family = {}
    for e in feed["entries"]:
        by_family.setdefault(e["family"], {})[e["source"]] = e["variants"]

    assert by_family["cedrlang-compression"] == {
        h: [c] for h, c in cedr.MAPPINGS}
    assert by_family["cedrlang-symbol"] == {
        p.strip(): [s.strip()] for p, s in cedr.SYMBOL_MAP.items()}
    assert set(by_family["cedrlang-stopwords"]) == set(cedr.STOPWORDS)
    assert by_family["phase-codec-leet-chars"] == {
        k: [v] for k, v in phase.LEET_MAP.items()}
    assert set(by_family["phase-codec-canonical-tokens"]) == \
        set(phase.CANONICAL_TOKENS)


def test_round_trip_flags_match_live_codecs():
    feed = _feed()
    # Compression mappings: fully reversible on the compile path.
    comp = [e for e in feed["entries"] if e["family"] == "cedrlang-compression"]
    assert comp and all(e["round_trip_verified"] is True for e in comp)
    # Phase tokens: fully reversible (case-insensitive) at p=1.0.
    toks = [e for e in feed["entries"]
            if e["family"] == "phase-codec-canonical-tokens"]
    assert toks and all(e["round_trip_verified"] is True for e in toks)
    for t in phase.CANONICAL_TOKENS:
        assert phase.from_1337speak(
            phase.to_1337speak(t, probability=1.0)).lower() == t.lower()
    # Symbols: re-derive every flag independently from the live pair.
    # (Lossiness comes from REV_MAP last-wins on duplicate symbols and
    # from substring collisions in expand(), e.g. ":=" contains "=".)
    syms = [e for e in feed["entries"] if e["family"] == "cedrlang-symbol"]
    assert syms
    for e in syms:
        phrase = next(p for p, s in cedr.SYMBOL_MAP.items()
                      if p.strip() == e["source"])
        symbol = cedr.SYMBOL_MAP[phrase]
        ok = (symbol.strip() in cedr.compress(f"x{phrase}y")
              and cedr.expand(f"x{symbol}y") == f"x{phrase}y")
        assert e["round_trip_verified"] is ok
        if not ok:
            assert e["note"]  # lossy entries must say why


def test_span_anchors_resolve():
    feed = _feed()
    for e in feed["entries"]:
        path = ROOT / e["provenance"]["path"]
        line = e["provenance"]["line"]
        assert line is not None and 1 <= line <= len(
            path.read_text(encoding="utf-8", errors="replace").splitlines())


def test_gaps_and_count_only_family_named():
    feed = _feed()
    gap_ids = {g["id"] for g in feed["gaps"]}
    assert "mapping-pointer-index-missing" in gap_ids
    arch = next(f for f in feed["families"]
                if f["id"] == "archwiz-pointer-index")
    assert arch["entries_included"] is False and arch["entry_count"] > 0
    assert not any(e["family"] == "archwiz-pointer-index"
                   for e in feed["entries"])
