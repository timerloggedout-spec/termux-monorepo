"""Collector tests for delphi-rfp-feed/v1 (synthetic cache fixtures)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "rfp_flood_feed", ROOT / "scripts" / "delphi" / "rfp_flood_feed.py")
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)

LEDGER = """<!-- delphi-ledger v1 -->
### Delphi round result: `research.example-lab`

**Award:** parked, recheck after 2026-11-27T03:02Z. Band Backlog.
**effective_score** 6.69 / 25 · converged False after 3 round(s) · trigger `opened`

| Round | Median | IQR | Effective |
|---|---|---|---|
| 1 | 9 | 6.0 | 7.38 |
| 2 | 9 | 6.0 | 6.92 |
| 3 | 9 | 6.0 | 6.69 |

Oracle: none - research lane ([source](https://example.invalid/issues/1))

```json
{"input_hash": "abc123", "effective_score": 6.69,
 "final_votes": [{"role": "OPERATOR", "score": 9, "impact": 3, "importance": 3,
                  "veto": false, "reason": "policy fit", "via": "rubric",
                  "signed": "Signed-off-by: Delphi-OPERATOR run-1 / #1#r3"}],
 "award": {"decision": "parked", "why": "below shadow bar", "band": "Backlog",
           "recheck_after": "2026-11-27T03:02Z"}}
```
"""

BODY = """intro

### Surface id

research.example-lab

### Lane

other

### Free quota

none - research lane

### Failure modes

- drift
"""


def _cache(tmp_path, issues, comments):
    (tmp_path / "issues.json").write_text(json.dumps(issues))
    (tmp_path / "comments.json").write_text(json.dumps(comments))
    (tmp_path / "surfaces.json").write_text(json.dumps({"surfaces": []}))
    (tmp_path / "panel.json").write_text(json.dumps({"roles": {"OPERATOR": {}}}))
    return tmp_path


def _issue(number, labels):
    return {"number": number, "title": "[delphi:rfp] research.example-lab",
            "html_url": f"https://example.invalid/issues/{number}",
            "created_at": "2026-10-27T00:00:00Z", "body": BODY,
            "labels": [{"name": n} for n in labels]}


def test_award_beats_converged_label(tmp_path):
    cache = _cache(tmp_path, [_issue(1, ["delphi:rfp", "delphi:parked", "delphi:converged"])],
                   {"1": [{"id": 9, "created_at": "2026-10-27T01:00:00Z", "body": LEDGER}]})
    out = feed.build(cache, "2026-10-27T00:00:00Z")
    (entry,) = out["rfps"]
    assert entry["status"] == "parked"          # the award, not the label mix
    assert entry["outcome"]["effective_score"] == 6.69
    assert entry["outcome"]["rounds"][2]["effective"] == 6.69
    assert entry["responses"]["votes"][0]["role"] == "OPERATOR"
    assert entry["group"] == "research-baseline"
    assert entry["comparison_axes"]["feature_extractions"].startswith("pending")
    assert out["summary"] == {"total_open": 1, "by_status": {"parked": 1},
                              "by_group": {"research-baseline": 1}}


def test_unscored_gap_named(tmp_path):
    cache = _cache(tmp_path, [_issue(2, ["delphi:rfp"])], {"2": []})
    out = feed.build(cache, "2026-10-27T00:00:00Z")
    (entry,) = out["rfps"]
    assert entry["status"] == "unscored"
    assert entry["outcome"] is None and entry["responses"] is None
    assert any("no gate ledger comment" in g for g in entry["gaps"])
    assert any("gantt_plan" in g for g in entry["gaps"])  # absent field, named


def test_partial_cache_refused(tmp_path):
    (tmp_path / "issues.json").write_text("[]")
    try:
        feed.build(tmp_path, "2026-10-27T00:00:00Z")
    except ValueError as e:
        assert "partial feed" in str(e)
    else:
        raise AssertionError("partial cache must be refused")
