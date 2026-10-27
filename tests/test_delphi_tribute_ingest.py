"""Tribute ingestion extractor (issue #1533): offline, stdlib-only."""
import json, os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.delphi import tribute_ingest


def _rec(url=None, sig=None):
    rec = {"subject": {"kind": "issue", "number": 1, "repo": "a/b"}}
    if url:
        rec["subject"]["url"] = url
    if sig is not None:
        rec["delphi_signal"] = sig
    return rec


def test_extract_keys_each_signal_by_thread_url():
    sig = {"surface": "tribute-lane", "repo": "a/b", "outcome": "merged", "weight": 1.0}
    out = tribute_ingest.extract([_rec("https://github.com/a/b/issues/1", sig)])
    assert out == [{"surface": "tribute-lane", "repo": "a/b",
                    "outcome": "merged", "weight": 1.0,
                    "key": "https://github.com/a/b/issues/1"}]


def test_extract_skips_signalless_records_and_flows_unkeyed():
    sig = {"surface": "tribute-lane", "repo": "a/b", "outcome": "merged"}
    out = tribute_ingest.extract([_rec(), _rec(None, sig), _rec(None, None)])
    assert len(out) == 1
    assert "key" not in out[0] and "weight" not in out[0]  # gate fills the weight
