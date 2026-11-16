"""QUE #5230: pin the bucket-headroom-watch workflow's shape."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "bucket-headroom-watch.yml"


def doc():
    return yaml.safe_load(WF.read_text())


def triggers(d):
    return d.get(True) or d.get("on")


def steps(d):
    return d["jobs"]["watch"]["steps"]


def test_schedule_and_inputs():
    on = triggers(doc())
    assert on["schedule"] == [{"cron": "*/10 * * * *"}]  # >= Cadence 5m floor
    inputs = on["workflow_dispatch"]["inputs"]
    assert inputs["dry_run"]["default"] is False
    assert inputs["drill"]["default"] is False


def test_permissions_and_concurrency():
    d = doc()
    assert d["permissions"] == {"contents": "write", "issues": "write"}
    assert d["concurrency"] == {"group": "bucket-headroom-watch",
                                "cancel-in-progress": False}


def test_mint_steps_for_provisioned_apps():
    text = WF.read_text()
    for role in ("SWARM", "COLLECTOR", "CROSSREFERENCE"):
        assert f"vars.TERMUX_FLEET_{role}_APP_ID" in text
        assert f"secrets.TERMUX_FLEET_{role}_PRIVATE_KEY" in text
    names = [s.get("name", "") for s in steps(doc())]
    assert names[0] == "Mint Swarm App token"
    assert "Mint Collector App token" in names
    assert "Mint CrossReference App token" in names


def test_collect_env_covers_all_bucket_classes():
    text = WF.read_text()
    for env in ("HEADROOM_PAT_TOKEN", "HEADROOM_GITHUB_TOKEN", "HEADROOM_SWARM_TOKEN",
                "HEADROOM_COLLECTOR_TOKEN", "HEADROOM_CROSSREFERENCE_TOKEN"):
        assert env in text
    assert "secrets.PAT_TOKEN" in text and "github.token" in text
    assert "bucket_headroom.py collect" in text


def test_evaluate_step_wiring():
    text = WF.read_text()
    assert "bucket_headroom.py evaluate" in text
    assert "--process ops/github-apps/PROCESS.json" in text
    assert "--previous ops/que/feeds/bucket-headroom.json" in text
    assert "--events-dir ops/que/events" in text
    assert "--drill" in text


def test_page_and_commit_steps():
    text = WF.read_text()
    assert "bucket-headroom-alert" in text  # standing-issue label
    assert "gh issue create" in text and "gh issue comment" in text
    assert "git add ops/que/feeds/bucket-headroom.json ops/que/events" in text
    assert "termux-fleet-swarm[bot]" in text


def test_receipt_and_failure_stamp():
    text = WF.read_text()
    assert "bucket-headroom-receipt" in text
    assert "bucket-headroom-watcher-error:v1" in text
    assert "gh issue comment 5230" in text


def test_step_order_collect_before_evaluate_before_page():
    names = [s.get("name", "") for s in steps(doc())]
    collect_i = next(i for i, n in enumerate(names) if "Collect bucket reads" in n)
    eval_i = next(i for i, n in enumerate(names) if "Evaluate headroom" in n)
    page_i = next(i for i, n in enumerate(names) if "Page standing issue" in n)
    commit_i = next(i for i, n in enumerate(names) if "Commit feed" in n)
    assert collect_i < eval_i < page_i < commit_i
