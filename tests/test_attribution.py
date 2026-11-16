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

def test_bold_trailers_grok_historical_form():
    pr = {**PR, "body": "**Agent:** Grok (xAI)\n**Signed-off-by:** Grok <grok@x.ai>"}
    r = at.extract_actor(pr)
    assert r["actor"] == "grok" and r["actor_evidence"]["method"] == "trailer"
    assert at.apply_registry(r["actor"]) == ("Grok", True)

def test_agent_identity_trailer_variants():
    def run(body):
        r = at.extract_actor({"number": 7, "title": "t", "body": body,
                              "user": {"login": "timerloggedout-spec"}})
        return r["actor"], r["actor_evidence"]["method"]
    assert run("body\nAgent-Identity: Runable\n") == ("runable", "trailer")
    assert run("Agent-Identity: Grok (Administrator) \u00b7 BIUDL") == ("grok", "trailer")
    assert run("Agent-Identity: ChatGPT / implementation steward") == ("chatgpt", "trailer")
    assert run("Agent-Identity: Hark") == ("hark", "trailer")
    assert run("Agent-Identity: Cue") == ("cue", "trailer")

def test_manifest_leg():
    pr = {"number": 9, "title": "t", "user": {"login": "timerloggedout-spec"},
          "body": "no marks"}
    files = [{"filename": "docs/proposals/active/chatgpt-initial/MANIFEST.md",
              "patch": "@@ -0,0 +1,6 @@\n+---\n+id: chatgpt-initial\n+author: ChatGPT\n+status: posted"}]
    r = at.extract_actor(pr, files=files)
    assert r["actor"] == "chatgpt" and r["actor_evidence"]["method"] == "manifest"
    pr2 = {**pr, "body": "---\nauthor: Manus\n---\nproposal"}
    assert at.extract_actor(pr2)["actor"] == "manus"
    code = [{"filename": "src/x.py", "patch": "+author: ChatGPT"}]
    assert at.extract_actor(pr, files=code)["actor"] is None
    own = [{"filename": "docs/proposals/active/z/MANIFEST.md", "patch": "+author: LoggedOut"}]
    assert at.extract_actor(pr, files=own)["actor"] is None

def test_corroboration_states():
    base = {"number": 3, "title": "t", "user": {"login": "timerloggedout-spec"}}
    r = at.extract_actor({**base, "body": "plain work"})
    assert r["corroboration"]["state"] == "unattributed"
    r = at.extract_actor({**base, "body": "Agent-Identity: Grok (Administrator)"})
    assert r["corroboration"]["state"] == "single-leg"
    commits = [{"commit": {"author": {"name": "Grok", "email": "grok@x.ai"}, "message": "x"}}]
    r = at.extract_actor({**base, "body": "Agent-Identity: Grok (Administrator)"}, commits)
    assert r["corroboration"]["state"] == "corroborated" and r["actor"] == "grok"
    r = at.extract_actor({**base, "body": "Agent-Identity: Manus"}, commits)
    assert r["corroboration"]["state"] == "disputed" and r["corroboration"]["conflicts"] == ["grok"]

def test_token_history_leg():
    bot = {"number": 5, "title": "t", "body": "",
           "user": {"login": "github-actions[bot]"}}
    r = at.extract_actor(bot)
    assert r["corroboration"]["state"] == "single-leg"
    r = at.extract_actor(bot, token_history={"merged_by": "github-actions[bot]"})
    assert r["corroboration"]["state"] == "corroborated"
    assert "token_history" in r["corroboration"]["agreeing"]
    r = at.extract_actor(bot, token_history={"merged_by": "timerloggedout-spec",
                                             "run_actors": ["github-actions[bot]"]})
    assert r["corroboration"]["state"] == "corroborated"
    # Jules shape: owner-merged, owner run actors -> stays single-leg
    jules = {**bot, "user": {"login": "google-labs-jules[bot]"}}
    r = at.extract_actor(jules, token_history={"merged_by": "timerloggedout-spec",
                                               "run_actors": ["timerloggedout-spec"]})
    assert r["corroboration"]["state"] == "single-leg"
    # token history never speaks for PAT riders / never conflicts
    human = {"number": 6, "title": "t", "body": "[MUSEai]@{role:{docs}}",
             "user": {"login": "timerloggedout-spec"}}
    r = at.extract_actor(human, token_history={"merged_by": "github-actions[bot]"})
    assert r["corroboration"]["state"] == "single-leg"
    assert "token_history" not in r["corroboration"]["legs"]
