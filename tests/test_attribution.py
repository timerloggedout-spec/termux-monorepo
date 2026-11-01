import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/telemetry_ingest/{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


at = _load("attribution")
ds = _load("density_stats")

PR = {"number": 1, "title": "x", "body": "", "state": "closed", "merged_at": "2026-01-01T00:00:00Z",
      "head": {"ref": "lane/x"}, "user": {"login": "timerloggedout-spec"}}


def test_stamp_wins():
    pr = {**PR, "body": "work done [MUSEai]@{role:{grok}} verified"}
    r = at.extract_actor(pr)
    assert r["actor"] == "grok" and r["actor_evidence"]["method"] == "stamp"


def test_owner_login_alone_is_null_never_owner_default():
    r = at.extract_actor(PR)
    assert r["actor"] is None and r["actor_evidence"]["method"] is None


def test_trailer_agent_and_signoff():
    pr = {**PR, "body": "notes\nAgent: Grok\n"}
    assert at.extract_actor(pr)["actor"] == "grok"
    pr2 = {**PR, "body": "x\nSigned-off-by: Grok <grok@x.ai>\n"}
    r = at.extract_actor(pr2)
    assert r["actor"] == "grok" and r["actor_evidence"]["method"] == "trailer"


def test_owner_signoff_is_not_collaborator_evidence():
    pr = {**PR, "body": "x\nSigned-off-by: timerloggedout-spec <timerloggedout@gmail.com>\n"}
    assert at.extract_actor(pr)["actor"] is None


def test_git_author_known_identity():
    commits = [{"commit": {"author": {"name": "Grok", "email": "grok@x.ai"}}}]
    r = at.extract_actor(PR, commits)
    assert r["actor"] == "grok" and r["actor_evidence"]["method"] == "git_author"


def test_git_author_unknown_name_stays_null():
    commits = [{"commit": {"author": {"name": "Some Random Tool", "email": "tool@example.org"}}}]
    assert at.extract_actor(PR, commits)["actor"] is None


def test_app_bot_login():
    pr = {**PR, "user": {"login": "termux-fleet-swarm[bot]"}}
    r = at.extract_actor(pr)
    assert r["actor"] == "termux-fleet-swarm" and r["actor_evidence"]["method"] == "app_bot"


def test_density_build_carries_actor_and_origin():
    prs = [{**PR, "number": n, "body": "b [MUSEai]@{role:{grok}} #1 merged"}
           for n in (1, 2, 3)]
    stats, payloads = ds.build(prs, {"rfps": []}, "2026-01-01T00:00:00Z",
                               origin={"kind": "backfill", "method_version": "attribution/1",
                                       "from": "2026-01-01", "to": "2026-02-01"})
    assert stats["attribution"]["attributed"] == 3
    assert stats["attribution"]["origin"]["kind"] == "backfill"
    assert any(p["metadata"].get("actor") == "Grok" for p in payloads)
    assert stats["per_actor"][0]["actor"] == "Grok"
