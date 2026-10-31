"""JIT phrase layer (scripts/doe/phrase_layer.py): leet anchor,
set matching, selection/placement/form behavior."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _layer():
    spec = importlib.util.spec_from_file_location(
        "phrase_layer", ROOT / "scripts/doe/phrase_layer.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


DATA = {"providers": {"deepseek": {
    "match": ["deepseek"],
    "prefixes": ["P1 ", "P2 "],
    "suffixes": ["Build the Future Now. Make it so.", "S2"],
    "profiles": {"1337": {"system_prefix": "PRE-1337",
                          "system_suffix": "SUF-1337"}}}}}


def test_leet_anchor_matches_established_profile_suffix():
    PL = _layer()
    assert PL.leet("Build the Future Now. Make it so.") == \
        "Bu1ld th3 Futur3 N0w. M4k3 1t s0."


def test_find_set_and_no_match():
    PL = _layer()
    assert PL.find_set(DATA, "openrouter/deepseek/deepseek-chat")[0] \
        == "deepseek"
    assert PL.find_set(DATA, "openrouter/openai/gpt-4o-mini") is None
    text, stamp = PL.apply_phrases("body", DATA,
                                   "openrouter/openai/gpt-4o-mini")
    assert text == "body" and stamp is None


def test_apply_first_prefix_suffix_and_leet_form():
    PL = _layer()
    text, stamp = PL.apply_phrases("body", DATA, "x/deepseek-v4")
    assert text == "P1\n\nbody\n\nBuild the Future Now. Make it so."
    assert stamp["provider"] == "deepseek"
    text2, _ = PL.apply_phrases("body", DATA, "x/deepseek-v4",
                                placement="suffix", form="leet")
    assert text2 == "body\n\nBu1ld th3 Futur3 N0w. M4k3 1t s0."


def test_hash_selection_is_deterministic():
    PL = _layer()
    a, _ = PL.apply_phrases("body", DATA, "x/deepseek-v4",
                            selection="hash")
    b, _ = PL.apply_phrases("body", DATA, "x/deepseek-v4",
                            selection="hash")
    assert a == b


def test_profile_overrides_lists():
    PL = _layer()
    text, stamp = PL.apply_phrases("body", DATA, "x/deepseek-v4",
                                   profile="1337")
    assert text == "PRE-1337\n\nbody\n\nSUF-1337"
    assert stamp["profile"] == "1337"


def test_token_forms_are_factor_levels_not_precedence():
    PL = _layer()
    # The owner's example kind: a casing/substitution ladder for
    # one token. Each rung is a LEVEL; the layer applies whichever
    # the design selects and stamps it.
    data = {"providers": {"deepseek": {
        "match": ["deepseek"], "prefixes": [],
        "suffixes": ["Do the thing. do it well."]}}}
    outs = {}
    for rung in ("d0", "DO", "Do", "do"):
        text, stamp = PL.apply_phrases(
            "body", data, "x/deepseek-v4", placement="suffix",
            token_forms={"do": rung})
        outs[rung] = text
        assert stamp["token_forms"] == {"do": rung}
    assert outs["d0"] == "body\n\nd0 the thing. d0 it well."
    assert outs["DO"] == "body\n\nDO the thing. DO it well."
    assert outs["do"] == "body\n\ndo the thing. do it well."
    assert len(set(outs.values())) == 4  # four distinct instances
