"""_v1_agent offline coverage (iteration 72).

Covers auth, job-registry projection, status phase transitions
(idle-hang detection), and path helpers.  All state is monkeypatched
onto a temp tree; nothing here touches the real ``~/.deepcli`` and no
subprocess is spawned.
"""

import json
import pathlib
import sys
import time
import unittest

HANG_MARGIN_S = 10  # push mtime this far past the hang threshold


def _repo_root():
    """Return the checkout that owns this test file's ``_v1_agent.py``.

    Walk up from __file__ to the directory that directly contains
    ``_v1_agent.py`` (the ``deepcli/`` package dir; ``tests/`` sits one
    level below it).  A ``$HOME/deepcli`` fallback preserves the old
    behaviour when no checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "_v1_agent.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
import _v1_agent as agent_mod
from fastapi import HTTPException


class _TmpLogdir(unittest.TestCase):
    """Base: redirect LOGDIR onto a temp dir for every test."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.logdir = pathlib.Path(self._tmp.name)
        self._orig_logdir = agent_mod.LOGDIR
        agent_mod.LOGDIR = self.logdir
        # keep the registry isolated per test
        self._orig_jobs = dict(agent_mod.JOBS)
        agent_mod.JOBS.clear()

    def tearDown(self):
        agent_mod.LOGDIR = self._orig_logdir
        agent_mod.JOBS.clear()
        agent_mod.JOBS.update(self._orig_jobs)
        self._tmp.cleanup()


class TestPathHelpers(_TmpLogdir):
    def test_log_path_name(self):
        p = agent_mod._job_log_path("abc123")
        self.assertEqual(p.name, "agent_abc123.log")
        self.assertEqual(p.parent, self.logdir)

    def test_meta_path_name(self):
        p = agent_mod._job_meta_path("abc123")
        self.assertEqual(p.name, "agent_abc123.meta.json")

    def test_logdir_created(self):
        import shutil; shutil.rmtree(self.logdir); self.assertFalse(self.logdir.exists())
        agent_mod._job_log_path("x")
        self.assertTrue(self.logdir.is_dir())


class TestWriteMeta(_TmpLogdir):
    def test_write_meta_roundtrip(self):
        agent_mod._write_meta("j1", {"phase": "running", "rc": None})
        raw = agent_mod._job_meta_path("j1").read_text()
        self.assertEqual(json.loads(raw)["phase"], "running")

    def test_write_meta_swallows_errors(self):
        # point LOGDIR at a path that cannot be a directory (a file)
        blocker = self.logdir / "blocker"
        blocker.write_text("x")
        agent_mod.LOGDIR = blocker
        agent_mod._write_meta("j1", {"phase": "x"})  # must not raise


class TestRequireAuth(unittest.TestCase):
    def setUp(self):
        self._orig_env = agent_mod.os.environ.pop("HUB_TOKEN", None)
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self._orig_token_file = agent_mod.TOKEN_FILE
        agent_mod.TOKEN_FILE = pathlib.Path(self._tmp.name) / "hub.token"

    def tearDown(self):
        if self._orig_env is not None:
            agent_mod.os.environ["HUB_TOKEN"] = self._orig_env
        else:
            agent_mod.os.environ.pop("HUB_TOKEN", None)
        agent_mod.TOKEN_FILE = self._orig_token_file
        self._tmp.cleanup()

    def test_missing_token_raises_500(self):
        with self.assertRaises(HTTPException) as cm:
            agent_mod._require_auth(None)
        self.assertEqual(cm.exception.status_code, 500)

    def test_valid_env_token(self):
        agent_mod.os.environ["HUB_TOKEN"] = "sekret"
        creds = type("C", (), {"credentials": "sekret"})()
        self.assertTrue(agent_mod._require_auth(creds))

    def test_bad_token_raises_401(self):
        agent_mod.os.environ["HUB_TOKEN"] = "sekret"
        creds = type("C", (), {"credentials": "nope"})()
        with self.assertRaises(HTTPException) as cm:
            agent_mod._require_auth(creds)
        self.assertEqual(cm.exception.status_code, 401)

    def test_none_creds_raises_401(self):
        agent_mod.os.environ["HUB_TOKEN"] = "sekret"
        with self.assertRaises(HTTPException) as cm:
            agent_mod._require_auth(None)
        self.assertEqual(cm.exception.status_code, 401)

    def test_token_from_file(self):
        agent_mod.TOKEN_FILE.write_text("filetok\n")
        creds = type("C", (), {"credentials": "filetok"})()
        self.assertTrue(agent_mod._require_auth(creds))


class TestAgentReq(unittest.TestCase):
    def test_defaults(self):
        r = agent_mod.AgentReq(task="do it")
        self.assertEqual(r.source, "unknown")
        self.assertFalse(r.dry_run)
        self.assertIsNone(r.context)
        self.assertIsNone(r.cwd)

    def test_explicit_fields(self):
        r = agent_mod.AgentReq(task="t", source="ci", dry_run=True)
        self.assertEqual(r.source, "ci")
        self.assertTrue(r.dry_run)


class TestJobList(_TmpLogdir):
    def test_empty(self):
        self.assertEqual(agent_mod._agent_list(), {"jobs": []})

    def test_sorted_newest_first(self):
        agent_mod.JOBS.update(
            {
                "old": {"invocation_id": "old", "phase": "done", "started_at": 100.0},
                "new": {
                    "invocation_id": "new",
                    "phase": "running",
                    "started_at": 200.0,
                },
            }
        )
        ids = [j["invocation_id"] for j in agent_mod._agent_list()["jobs"]]
        self.assertEqual(ids, ["new", "old"])

    def test_projection_keys_only(self):
        agent_mod.JOBS["a"] = {
            "invocation_id": "a",
            "phase": "running",
            "source": "ci",
            "task_head": "x",
            "rc": None,
            "elapsed_s": 1.0,
            "pid": 999,  # must NOT leak into list output
        }
        got = agent_mod._agent_list()["jobs"][0]
        self.assertEqual(
            set(got),
            {
                "invocation_id",
                "phase",
                "source",
                "task_head",
                "rc",
                "elapsed_s",
            },
        )

    def test_capped_at_twenty(self):
        for i in range(25):
            agent_mod.JOBS[f"j{i}"] = {"invocation_id": f"j{i}", "started_at": float(i)}
        self.assertEqual(len(agent_mod._agent_list()["jobs"]), 20)
        # newest (j24) must be first
        self.assertEqual(agent_mod._agent_list()["jobs"][0]["invocation_id"], "j24")


class TestStatusPhase(_TmpLogdir):
    def test_unknown_invocation_raises_404(self):
        with self.assertRaises(HTTPException) as cm:
            agent_mod._agent_status("nope")
        self.assertEqual(cm.exception.status_code, 404)

    def test_unknown_phase_when_meta_only(self):
        agent_mod._job_meta_path("m1").write_text(json.dumps({"phase": "running"}))
        out = agent_mod._agent_status("m1")
        self.assertEqual(out["invocation_id"], "m1")
        # no in-memory job -> phase defaults to "unknown"
        self.assertEqual(out["phase"], "unknown")

    def test_tail_is_last_25_lines(self):
        log = agent_mod._job_log_path("t1")
        log.write_text("\n".join(f"line{i}" for i in range(40)))
        out = agent_mod._agent_status("t1")
        self.assertEqual(len(out["tail"]), 25)
        self.assertEqual(out["tail"][-1], "line39")

    def test_running_not_hung_when_fresh(self):
        agent_mod.JOBS["h1"] = {
            "invocation_id": "h1",
            "phase": "running",
            "started_at": time.time(),
        }
        agent_mod._job_log_path("h1").write_text("working\n")  # mtime = now
        out = agent_mod._agent_status("h1")
        self.assertEqual(out["phase"], "running")

    def test_running_hung_when_idle(self):
        agent_mod.JOBS["h2"] = {
            "invocation_id": "h2",
            "phase": "running",
            "started_at": time.time(),
        }
        log = agent_mod._job_log_path("h2")
        log.write_text("stalled\n")
        # backdate mtime well past the threshold
        past = time.time() - agent_mod.IDLE_HANG_THRESHOLD_S - HANG_MARGIN_S
        agent_mod.os.utime(log, (past, past))
        out = agent_mod._agent_status("h2")
        self.assertEqual(out["phase"], "possibly_hung")

    def test_done_phase_never_flagged_hung(self):
        agent_mod.JOBS["d1"] = {
            "invocation_id": "d1",
            "phase": "done",
            "started_at": time.time() - 1000,
            "rc": 0,
        }
        log = agent_mod._job_log_path("d1")
        log.write_text("finished\n")
        past = time.time() - agent_mod.IDLE_HANG_THRESHOLD_S - HANG_MARGIN_S
        agent_mod.os.utime(log, (past, past))
        out = agent_mod._agent_status("d1")
        self.assertEqual(out["phase"], "done")
        self.assertEqual(out["rc"], 0)

    def test_rc_falls_back_to_meta(self):
        log = agent_mod._job_log_path("r1")
        log.write_text("x\n")
        agent_mod._job_meta_path("r1").write_text(json.dumps({"rc": 7}))
        out = agent_mod._agent_status("r1")
        self.assertEqual(out["rc"], 7)


class TestKill(_TmpLogdir):
    def test_unknown_job_raises_404(self):
        with self.assertRaises(HTTPException) as cm:
            agent_mod._agent_kill("nope")
        self.assertEqual(cm.exception.status_code, 404)

    def test_no_pid_returns_not_killed(self):
        agent_mod.JOBS["k1"] = {"invocation_id": "k1", "phase": "running"}
        self.assertEqual(
            agent_mod._agent_kill("k1"), {"killed": False, "reason": "no pid yet"}
        )


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "_v1_agent.py").is_file())
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


if __name__ == "__main__":
    unittest.main()
