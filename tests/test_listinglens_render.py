"""Tests for the ListingLens video-render helpers (#5137).

Run: python3 -m pytest tests/test_listinglens_render.py
The decidable legs only: beats-manifest derivation from a real demo
capture (values must come from the run, never constants) and the
render receipt shape. ffmpeg assembly is exercised by the workflow's
own live run (done-evidence on #5137).
"""

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "listinglens"))
from build_receipt import build_receipt
from derive_manifest import derive

# Captured verbatim from `node apps/listinglens/demo/run-demo.mjs`
# on master (2026-11-12). If the demo's output changes, this fixture
# must be re-captured, not hand-edited to pass.
DEMO_OUTPUT = """== ListingLens demo: photo ↦ listing ==
photo        sample-vase.svg (sample-vase-001)
title        Hand-Thrown Terracotta Glaze Stoneware Vase
description  Hand-Thrown Terracotta Glaze Stoneware Vase — a one-of-a-kind piece from an independent maker. Condition: like new, carefully kept. Photographed as-is; what you see is the exact item that ships. Seller notes: Thrown on my wheel in March; food-safe glaze, watertight.
bullets      Condition: like new, carefully kept | Hand-Thrown | Stoneware | Terracotta Glaze | Palette: #b5542d, #e8dcc8, #3e2f25 | Ships from the maker's studio, packed by hand
price        $56.99 (range $54.00–$62.00, basis comparables)
price why    Median of 4 comparable sold listings, × 1 condition factor (like-new).
layout       hero-spotlight · accent #b5542d · sections hero → story → details → shipping
provenance   listinglens-local/1 (deterministic fallback) · rev 1

== seller edit/act ↦ revision ==
title        Terracotta Stoneware Vase — Small Batch, Signed
price        $64.99
provenance   rev 2

DEMO OK — end-to-end, offline, deterministic.
"""

ACTIONS_SRC = """
export const generateListingAction = defineAction({
export const reviseListingAction = defineAction({
"""

REPO_URL = "https://github.com/timerloggedout-spec/termux-monorepo"


def test_manifest_values_come_from_the_run():
    m = derive(DEMO_OUTPUT, ACTIONS_SRC, REPO_URL)
    assert m["schema"] == "listinglens.beats/v1"
    assert len(m["beats"]) == 5
    assert m["values"] == {
        "title_rev1": "Hand-Thrown Terracotta Glaze Stoneware Vase",
        "price_rev1": "$56.99",
        "title_rev2": "Terracotta Stoneware Vase — Small Batch, Signed",
        "price_rev2": "$64.99",
    }
    assert m["accent"] == "#b5542d"
    assert m["template"] == "hero-spotlight"
    assert m["model"] == "listinglens-local/1"
    beat2 = " ".join(m["beats"][1]["lines"])
    assert "$56.99" in beat2 and "hero-spotlight" in beat2
    beat5 = " ".join(m["beats"][4]["lines"])
    assert "generateListingAction" in beat5 and "reviseListingAction" in beat5
    assert REPO_URL in beat5


def test_manifest_fails_closed_on_missing_values():
    with pytest.raises(ValueError):
        derive("title        only a title\n", ACTIONS_SRC, REPO_URL)
    with pytest.raises(ValueError):
        derive(DEMO_OUTPUT, "export const oneAction = defineAction({", REPO_URL)


def test_receipt_shape(tmp_path):
    mp4 = tmp_path / "listinglens-demo.mp4"
    mp4.write_bytes(b"fake-mp4-bytes")
    manifest = derive(DEMO_OUTPUT, ACTIONS_SRC, REPO_URL)
    receipt = build_receipt(
        mp4, {"format": {"duration": "15.033333"}}, manifest,
        "43219999999", "https://example.invalid/runs/43219999999")
    assert receipt["schema"] == "listinglens.render-receipt/v1"
    assert receipt["mp4"] == "listinglens-demo.mp4"
    assert receipt["sha256"] == hashlib.sha256(b"fake-mp4-bytes").hexdigest()
    assert receipt["duration_s"] == 15.03
    assert receipt["capture_run_id"] == "43219999999"
    assert receipt["beats"] == 5
    assert receipt["values"]["price_rev2"] == "$64.99"
