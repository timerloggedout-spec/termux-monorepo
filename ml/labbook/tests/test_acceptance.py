"""Acceptance tests for labbook v1 — §3's validation plan, applied to our
own build at the same bar the ten researched platforms were held to:

  1. Gate honesty (the Kubeflow trap, replayed against ourselves).
  2. Round trip: a cold process re-derives the headline exactly, API only.
  3. Comparison: two runs, server-free, with computed deltas.
  4. Cache semantics: identical re-run all-cached + run record written;
     one-key param change rebuilds only dependents.
  5. Amnesia: kill the runner mid-run; the ledger tells the truth cold.
  6. Bundle self-sufficiency: verify from the zip alone, bit-exact.
  7. Formats: declared everywhere; pickle-class flagged in the record.

Run: python -m unittest discover -s tests -v
"""

import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_PARENT = os.path.join(HERE, "..")
sys.path.insert(0, PKG_PARENT)

from labbook.api import Labbook
from labbook.compiler import Node, Pipeline
from labbook.errors import LabbookError

DEMO_DIR = os.path.join(PKG_PARENT, "demo")

FUNCS = '''
import time

def produce(ctx, inputs, params):
    ctx.log_metric("score", params["score"])
    return {"a": "value-a"}

def boom(ctx, inputs, params):
    raise RuntimeError("boom-gate-marker")

def gated(ctx, inputs, params):
    return {"b": "value-b"}

def consume(ctx, inputs, params):
    return {"c": "saw:" + inputs["b"]}

def first(ctx, inputs, params):
    return {"a1": "first-done"}

def slow(ctx, inputs, params):
    time.sleep(30)
    return {"a2": "never"}
'''


def scaffold(files):
    td = tempfile.mkdtemp(prefix="labbook-test-")
    for name, content in files.items():
        with open(os.path.join(td, name), "w") as f:
            f.write(content)
    return td


def demo_project():
    td = tempfile.mkdtemp(prefix="labbook-demo-")
    for name in ("catalog.yml", "pipeline.py"):
        shutil.copy(os.path.join(DEMO_DIR, name), os.path.join(td, name))
    return td


class DemoRun:
    """One shared demo run for the read-side acceptance tests."""

    _cache = {}

    @classmethod
    def get(cls):
        if "run" not in cls._cache:
            project = demo_project()
            sys.path.insert(0, project)
            try:
                import pipeline

                lb = Labbook(project)
                ir = lb.compile(pipeline.PIPELINE)
                verdict = lb.run(ir, actor="acceptance")
                cls._cache.update(project=project, lb=lb, ir=ir,
                                  verdict=verdict)
            finally:
                sys.path.remove(project)
        return cls._cache


class TestRoundTrip(unittest.TestCase):
    def test_verdict_enumerates_every_node_and_gate_ran(self):
        d = DemoRun.get()
        v = d["verdict"]
        self.assertTrue(v["ok"], v)
        states = {(n["node_name"], n["instance"]): n["state"]
                  for n in v["nodes"]}
        self.assertEqual(states[("load", "")], "ran")
        self.assertEqual(states[("join", "")], "ran")
        # The Kubeflow trap, mirrored: the gate condition is TRUE, so the
        # gated node must have EXECUTED — a vanished branch under a
        # success verdict is exactly what this build exists to refuse.
        self.assertEqual(states[("report", "")], "ran")
        for fold in range(5):
            self.assertEqual(states[("train_quadratic", f"fold={fold}")],
                             "ran")
        self.assertEqual(v["headline"]["cv_mean_quad"],
                         d["lb"].latest("cv_metrics")
                         ["typed_metadata"]["cv_mean_quad"])

    def test_cold_process_rederives_headline_exactly(self):
        d = DemoRun.get()
        script = (
            "import json,sys;"
            "sys.path.insert(0, sys.argv[1]);"
            "from labbook.api import Labbook;"
            "lb = Labbook(sys.argv[2]);"
            "res = lb.verify(sys.argv[3]);"
            "print(json.dumps({'pass': res['pass'],"
            " 'headline': lb.get_run(sys.argv[3])['headline']}))"
        )
        out = subprocess.run(
            [sys.executable, "-c", script, PKG_PARENT, d["project"],
             d["verdict"]["run_id"]],
            capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout.strip())
        self.assertTrue(got["pass"])
        self.assertEqual(got["headline"], d["verdict"]["headline"])

    def test_verify_checks_all_named_and_passing(self):
        d = DemoRun.get()
        res = d["lb"].verify(d["verdict"]["run_id"])
        self.assertTrue(res["pass"], res["checks"])
        names = {c["check"] for c in res["checks"]}
        self.assertIn("headline-recompute", names)
        self.assertIn("fold-metrics-match-stored-parts", names)
        self.assertIn("node-enumeration", names)


class TestFormatsOnRun(unittest.TestCase):
    def test_pickle_class_flagged_in_record(self):
        d = DemoRun.get()
        lb = d["lb"]
        mats = lb.materializations("legacy_blob")
        self.assertEqual(len(mats), 1)
        self.assertIs(mats[0]["typed_metadata"].get("pickle_class"), True)
        asset = lb.ledger.asset_by_name("legacy_blob")
        self.assertEqual(asset["format"], "pickle-class")
        for name in ("dataset", "cv_metrics", "report"):
            for m in lb.materializations(name):
                self.assertTrue(m["reader"].startswith("labbook.formats:"))


class TestCompare(unittest.TestCase):
    def test_compare_two_runs_server_free(self):
        d = DemoRun.get()
        lb, project = d["lb"], d["project"]
        sys.path.insert(0, project)
        try:
            import pipeline

            v2 = lb.run(d["ir"], params={"ridge": 5.0}, actor="acceptance")
        finally:
            sys.path.remove(project)
        self.assertTrue(v2["ok"], v2)
        diff = lb.compare(d["verdict"]["run_id"], v2["run_id"])
        self.assertEqual(diff["params"]["ridge"],
                         {"a": 0.1, "b": 5.0, "changed": True})
        self.assertFalse(diff["params"]["seed"]["changed"])
        self.assertTrue(diff["artifacts"]["dataset"]["same"])
        self.assertFalse(diff["artifacts"]["fold_models_quad"]["same"])
        m = diff["metrics"]["cv_mean_quad"]
        self.assertEqual(m["delta"], m["b"] - m["a"])
        self.assertNotEqual(m["delta"], 0.0)


class TestCacheSemantics(unittest.TestCase):
    def test_identical_rerun_all_cached_and_param_change_partial(self):
        project = demo_project()
        sys.path.insert(0, project)
        try:
            import pipeline

            lb = Labbook(project)
            ir = lb.compile(pipeline.PIPELINE)
            v1 = lb.run(ir, actor="cache-test")
            self.assertTrue(v1["ok"], v1)
            v2 = lb.run(ir, actor="cache-test")
            self.assertTrue(v2["ok"], v2)
            states2 = {n["node_name"]: n["state"] for n in v2["nodes"]
                       if n["instance"] == ""}
            self.assertTrue(
                all(n["state"] == "cached" for n in v2["nodes"]),
                [(n["node_name"], n["instance"], n["state"])
                 for n in v2["nodes"]])
            # A fully cached run still writes its own run record (row 9).
            rec2 = lb.get_run(v2["run_id"])
            self.assertEqual(rec2["lifecycle"], "completed")
            self.assertEqual(rec2["headline"], v1["headline"])
            v3 = lb.run(ir, params={"ridge": 2.0}, actor="cache-test")
            self.assertTrue(v3["ok"], v3)
            by_node = {}
            for n in v3["nodes"]:
                by_node.setdefault(n["node_name"], set()).add(n["state"])
            self.assertEqual(by_node["load"], {"cached"})
            self.assertEqual(by_node["train_linear"], {"ran"})
            self.assertEqual(by_node["train_quadratic"], {"ran"})
            self.assertEqual(by_node["join"], {"ran"})
            lb.close()
        finally:
            sys.path.remove(project)


CATALOG_AB = {
    "a": {"kind": "dataset", "format": "text"},
    "b": {"kind": "dataset", "format": "text"},
    "c": {"kind": "report", "format": "text"},
    "a1": {"kind": "dataset", "format": "text"},
    "a2": {"kind": "dataset", "format": "text"},
}


def small_lb(files_extra=None, catalog=None):
    files = {"funcs.py": FUNCS}
    files.update(files_extra or {})
    project = scaffold(files)
    from labbook.catalog import Catalog

    lb = Labbook(project, catalog=Catalog.from_dict(catalog or CATALOG_AB))
    return lb, project


class TestGateHonesty(unittest.TestCase):
    def test_gate_true_and_node_fails_verdict_names_it(self):
        lb, _ = small_lb()
        pipe = Pipeline(
            "trap", params={"score": {"type": "float", "default": 0.5}},
            cache_policy="per-artifact-store",
            nodes=[
                Node("produce", "funcs:produce", outputs=["a"],
                     params=["score"]),
                Node("gated", "funcs:boom", inputs={"a": "one"},
                     outputs=["b"], gate="score < 1.0"),
                Node("consume", "funcs:consume", inputs={"b": "one"},
                     outputs=["c"]),
            ])
        v = lb.run(lb.compile(pipe))
        # NOT a bare success: lifecycle failed, the node named, its error
        # verbatim, the downstream node enumerated as not-run.
        self.assertFalse(v["ok"])
        self.assertEqual(v["lifecycle"], "failed")
        states = {n["node_name"]: n for n in v["nodes"]}
        self.assertEqual(states["gated"]["state"], "failed")
        self.assertIn("boom-gate-marker", states["gated"]["error"])
        self.assertEqual(states["consume"]["state"], "not-run")
        lb.close()

    def test_gate_false_skips_by_name_with_inputs(self):
        lb, _ = small_lb()
        pipe = Pipeline(
            "gated", params={"score": {"type": "float", "default": 2.0}},
            cache_policy="per-artifact-store",
            nodes=[
                Node("produce", "funcs:produce", outputs=["a"],
                     params=["score"]),
                Node("gated", "funcs:gated", inputs={"a": "one"},
                     outputs=["b"], gate="score < 1.0"),
                Node("consume", "funcs:consume", inputs={"b": "one"},
                     outputs=["c"]),
            ])
        v = lb.run(lb.compile(pipe))
        self.assertTrue(v["ok"], v)
        states = {n["node_name"]: n for n in v["nodes"]}
        g = states["gated"]
        self.assertEqual(g["state"], "skipped-by-gate")
        self.assertEqual(g["gate_expression"], "score < 1.0")
        self.assertEqual(g["gate_inputs"], {"score": 2.0})
        self.assertEqual(states["consume"]["state"], "skipped-by-gate")
        lb.close()

    def test_unsupported_construct_refused_by_name_before_running(self):
        lb, _ = small_lb()
        pipe = Pipeline(
            "bad", cache_policy="per-artifact-store",
            nodes=[Node("q", "funcs:produce", outputs=["a"], kind="python")])
        ir = lb.compile(pipe)
        ir["nodes"][0]["kind"] = "quantum"
        with self.assertRaises(LabbookError) as cm:
            lb.run(ir)
        self.assertIn("quantum", str(cm.exception))
        n = lb.ledger.conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        self.assertEqual(n, 0)
        lb.close()


class TestAmnesia(unittest.TestCase):
    def test_killed_runner_leaves_true_record(self):
        project = scaffold({"funcs.py": FUNCS})
        driver = os.path.join(project, "driver.py")
        with open(driver, "w") as f:
            f.write(
                "import sys\n"
                f"sys.path.insert(0, {PKG_PARENT!r})\n"
                f"sys.path.insert(0, {project!r})\n"
                "from labbook.api import Labbook\n"
                "from labbook.catalog import Catalog\n"
                "from labbook.compiler import Node, Pipeline\n"
                "cat = Catalog.from_dict({'a1': {'kind': 'dataset',"
                " 'format': 'text'}, 'a2': {'kind': 'dataset',"
                " 'format': 'text'}})\n"
                "lb = Labbook(sys.argv[1], catalog=cat)\n"
                "pipe = Pipeline('amnesia',"
                " cache_policy='per-artifact-store', nodes=["
                " Node('first', 'funcs:first', outputs=['a1']),"
                " Node('slow', 'funcs:slow', inputs={'a1': 'one'},"
                " outputs=['a2'])])\n"
                "lb.run(lb.compile(pipe))\n"
            )
        proc = subprocess.Popen(
            [sys.executable, driver, project],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        db = os.path.join(project, ".labbook", "ledger.db")
        deadline = time.time() + 30
        killed = False
        try:
            while time.time() < deadline:
                if os.path.exists(db):
                    conn = sqlite3.connect(db)
                    try:
                        rows = conn.execute(
                            "SELECT COUNT(*) FROM materializations").fetchone()
                        if rows and rows[0] >= 1:
                            break
                    except sqlite3.OperationalError:
                        pass
                    finally:
                        conn.close()
                time.sleep(0.2)
            time.sleep(1.0)  # the slow node is now mid-sleep
            os.killpg(proc.pid, signal.SIGKILL)
            killed = True
        finally:
            if not killed:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        # Cold process, nothing running: the record must tell the truth.
        from labbook.catalog import Catalog

        lb = Labbook(project, catalog=Catalog.from_dict(
            {"a1": {"kind": "dataset", "format": "text"},
             "a2": {"kind": "dataset", "format": "text"}}))
        runs = lb.ledger.conn.execute("SELECT run_id FROM runs").fetchall()
        self.assertEqual(len(runs), 1)
        rec = lb.get_run(runs[0][0])
        self.assertEqual(rec["lifecycle"], "running")
        states = {n["node_name"]: n["state"] for n in rec["nodes"]}
        self.assertEqual(states.get("first"), "ran")
        self.assertNotEqual(states.get("slow"), "ran")
        mats = lb.materializations("a1")
        self.assertEqual(len(mats), 1)
        self.assertEqual(lb.cas.get(mats[0]["content_hash"]), b"first-done")
        lb.close()


class TestBundle(unittest.TestCase):
    def test_bundle_verifies_alone_and_tamper_fails(self):
        d = DemoRun.get()
        lb = d["lb"]
        out = os.path.join(tempfile.mkdtemp(), "run.zip")
        lb.export_bundle(d["verdict"]["run_id"], out)
        script = (
            "import json,sys;"
            "sys.path.insert(0, sys.argv[1]);"
            "from labbook.api import Labbook;"
            "print(json.dumps(Labbook.verify_bundle(sys.argv[2])['pass']))"
        )
        res = subprocess.run([sys.executable, "-c", script, PKG_PARENT, out],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout.strip()), True)
        # Tamper: flip one artifact byte inside a copy.
        bad = out + ".bad"
        with zipfile.ZipFile(out) as zin, zipfile.ZipFile(
                bad, "w") as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item.startswith("artifacts/"):
                    data = data[:-1] + bytes([data[-1] ^ 0xFF])
                zout.writestr(item, data)
        res = Labbook.verify_bundle(bad)
        self.assertFalse(res["pass"], res["checks"])


class TestCLI(unittest.TestCase):
    def test_catalog_list_and_verify_bundle_verbs(self):
        d = DemoRun.get()
        env = dict(os.environ)
        env["PYTHONPATH"] = PKG_PARENT + os.pathsep + d["project"]
        out = subprocess.run(
            [sys.executable, "-m", "labbook", "--project", d["project"],
             "catalog", "list"],
            capture_output=True, text=True, env=env, cwd=d["project"])
        self.assertEqual(out.returncode, 0, out.stderr)
        names = {e["name"] for e in json.loads(out.stdout)}
        self.assertIn("dataset", names)
        self.assertIn("legacy_blob", names)


if __name__ == "__main__":
    unittest.main()
