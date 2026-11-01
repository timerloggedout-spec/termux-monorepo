"""Tests for the live-3 dispatcher automation (rule 5, WO-A)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "live3_dispatcher", ROOT / "scripts/doe/live3_dispatcher.py")
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)
SCHEMA = json.loads(
    (ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())

PHRASES = {"providers": {"deepseek": {
    "match": ["deepseek"],
    "prefixes": ["Build the Future Now. Make it so."],
    "suffixes": ["Show me what you got. GB"]}},
    "char_variants": {}, "established_vowel_map":
    {"a": "4", "e": "3", "i": "1", "o": "0"}}


def test_active_cells_never_leet():
    assert all("leet" not in c for c in D.ACTIVE_CELLS)
    assert len(D.ACTIVE_CELLS) == 7  # 6 phrased + control


def test_assignment_deterministic_and_in_set():
    for pr in (2436, 2800, 1234, 99999):
        idx, cell = D.assign_cell(pr)
        assert cell == D.ACTIVE_CELLS[idx]
        assert D.assign_cell(pr) == (idx, cell)


def test_compose_vowels_transforms_phrase_only():
    composed, stamp, cfg = D.compose("Review the PR body.", 
                                     "suffix-vowels", PHRASES)
    assert composed.startswith("Review the PR body.")
    assert "Sh0w m3 wh4t y0u g0t. GB" in composed
    assert stamp["suffix_sha256_12"] is not None


def test_compose_control_is_unphrased():
    composed, stamp, cfg = D.compose("Review the PR body.",
                                     "control", PHRASES)
    assert composed == "Review the PR body."
    assert stamp is None


def test_exclusions_from_records(tmp_path):
    live1 = tmp_path / "live1"
    cb1 = tmp_path / "cb1"
    live1.mkdir()
    cb1.mkdir()
    (live1 / "r1.json").write_text(json.dumps(
        {"metrics": {"pr": 2436}}))
    (cb1 / "r2.json").write_text(json.dumps(
        {"metrics": {"target_pr": 777}}))
    assert D.excluded_prs(live1, cb1, {}) == {2436, 777}
    assert D.excluded_prs(live1, cb1,
                          {"automation": {"extra_excluded_prs": [5]}}) \
        == {2436, 777, 5}


def _plan_args(tmp_path, pr):
    design = tmp_path / "DESIGN.json"
    design.write_text(json.dumps({"automation": {"daily_call_cap": 2}}))
    phrases = tmp_path / "phrases.json"
    phrases.write_text(json.dumps(PHRASES))
    task = tmp_path / "task.md"
    task.write_text("Review this pull request carefully.")
    empty = tmp_path / "none"
    empty.mkdir(exist_ok=True)
    return SimpleNamespace(
        pr=pr, pr_head="c" * 40, task_file=str(task),
        design=str(design), phrases=str(phrases),
        live1_records=str(empty), cb1_records=str(empty),
        dispatch_dir=str(tmp_path / "dispatch"),
        state=str(tmp_path / "dispatch" / "state.json"))


def test_plan_writes_stamped_job(tmp_path):
    args = _plan_args(tmp_path, 2436)
    assert D.cmd_plan(args) == 0
    job = json.loads(
        (tmp_path / "dispatch" / "job-0001-pr2436.json").read_text())
    assert job["schema"] == "doe-phrase-dispatch/v1"
    assert job["assignment"]["cell"] in D.ACTIVE_CELLS
    assert job["prompt_sha256"]
    assert job["instance_key"]
    assert job["task"]["screening"]["live1_designed"] is False


def test_plan_budget_exhausted(tmp_path):
    args = _plan_args(tmp_path, 2436)
    assert D.cmd_plan(args) == 0
    assert D.cmd_record(_record_args(tmp_path)) == 0
    assert D.cmd_record(_record_args(tmp_path, no=1)) == 0
    assert D.cmd_plan(_plan_args(tmp_path, 3000)) == 5


def _record_args(tmp_path, no=1):
    job = tmp_path / "dispatch" / f"job-{no:04d}-pr2436.json"
    if not job.exists():
        job.write_text(json.dumps({
            "dispatch_no": no, "campaign_id": D.CAMPAIGN,
            "assignment": {"cell": "control"},
            "task": {"pr": 2436, "pr_head": "c" * 40},
            "instance_key": "k", "prompt_sha256": "p" * 64}))
    result = tmp_path / "result.json"
    result.write_text(json.dumps({
        "status": "ok", "finished_at": "2026-11-03T00:00:00Z",
        "response_sha256": "r" * 64, "response_chars": 42}))
    return SimpleNamespace(
        job=str(job), result=str(result),
        records_dir=str(tmp_path / "records"),
        summary=str(tmp_path / "SUMMARY.json"),
        state=str(tmp_path / "dispatch" / "state.json"),
        base_sha="c" * 40)


def test_record_schema_and_summary(tmp_path):
    args = _plan_args(tmp_path, 2436)
    assert D.cmd_plan(args) == 0
    assert D.cmd_record(_record_args(tmp_path)) == 0
    rec = json.loads(
        (tmp_path / "records" / "dispatch-0001.json").read_text())
    jsonschema.validate(rec, SCHEMA)
    assert rec["status"] == "passed"
    assert rec["treatment"]["arm"] in D.ACTIVE_CELLS
    summary = json.loads((tmp_path / "SUMMARY.json").read_text())
    assert summary["runs"] == 1
