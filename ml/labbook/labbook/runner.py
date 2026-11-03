"""The local runner (ledger rows 6, 7, 9, 12, 13).

Semantics-faithful or refuses by name: any IR construct the runner cannot
execute is a hard error listing the construct, *before anything runs*
(Kubeflow's silently-amputated graph is the refused behavior). Every
run's verdict enumerates every node instance with an explicit state
(ran / cached / skipped-by-gate / failed / not-run / not-supported),
with the gate expression and its evaluated inputs for any skip.

The run row and its lifecycle stamps are written before and during
execution — never scraped post-hoc — so a killed runner still leaves a
true record (the amnesia test, §3).
"""

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import time

from . import compiler, formats, gates
from .cas import sha256_bytes
from .errors import LabbookError

SUPPORTED_KINDS = ("python",)


def capture_env() -> str:
    """Environment capture is automatic (row 12): python, platform, and
    the installed distribution set, on every run, without being asked."""
    pkgs = {}
    try:
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name")
            if name:
                pkgs[name] = dist.version
    except Exception:
        pkgs = {}
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": pkgs,
    }
    return json.dumps(env, sort_keys=True)


def capture_code_sha(project_dir: str, ir: dict) -> str:
    """Code identity is a mandatory structured field (row 12): the git
    SHA when the project is a checkout, else the content hash of the
    node modules' sources. Never a tag convention, never absent."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=project_dir,
            capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return "git:" + out.stdout.strip()
    except Exception:
        pass
    h = hashlib.sha256()
    for node in ir.get("nodes") or []:
        module = (node.get("func") or "").split(":")[0]
        rel = module.replace(".", "/") + ".py"
        for base in (project_dir, os.getcwd()):
            path = os.path.join(base, rel)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    h.update(f.read())
                break
    return "content:" + h.hexdigest()


def _func_source_hash(func: str, project_dir: str) -> str:
    module = func.split(":")[0]
    rel = module.replace(".", "/") + ".py"
    pkg = module.replace(".", "/") + "/__init__.py"
    for base in [project_dir] + sys.path:
        for cand in (rel, pkg):
            path = os.path.join(base, cand)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return sha256_bytes(f.read())
    raise LabbookError(
        "node function module not found on the path",
        value=func,
        expected="the module importable from the project directory",
        fix="run from the project root, or put the module on PYTHONPATH",
    )


def precheck(ir: dict):
    """Refuse unsupported constructs by name, before anything runs."""
    problems = []
    if ir.get("schemaVersion") != compiler.IR_SCHEMA:
        problems.append(f"schemaVersion {ir.get('schemaVersion')!r}")
    for node in ir.get("nodes") or []:
        if node.get("kind") not in SUPPORTED_KINDS:
            problems.append(
                f"node {node.get('name')!r} kind {node.get('kind')!r}")
        for spec in node.get("inputs") or []:
            if spec.get("mode") not in ("one", "all"):
                problems.append(
                    f"node {node.get('name')!r} input mode {spec.get('mode')!r}")
        fe = node.get("foreach")
        if fe is not None and not isinstance(fe, dict):
            problems.append(f"node {node.get('name')!r} foreach shape")
    if problems:
        raise LabbookError(
            "IR contains constructs this runner does not execute",
            value=problems,
            expected="labbook/1 constructs: python nodes, one/all inputs, "
            "mapping foreach",
            fix="remove or replace the named constructs; the runner never "
            "silently drops part of a graph (row 6)",
        )


def _instance_label(foreach, value):
    return f"{foreach['param']}={value}"


def _aggregate(ir, ledger, run_id):
    headline = {}
    for name, agg in (ir.get("aggregates") or {}).items():
        events = ledger.metric_events(run_id, name=agg["metric"],
                                      node_name=agg["node"])
        values = [e["value"] for e in events]
        if not values:
            continue
        op = agg["op"]
        if op == "mean":
            headline[name] = sum(values) / len(values)
        elif op == "sum":
            headline[name] = sum(values)
        elif op == "min":
            headline[name] = min(values)
        elif op == "max":
            headline[name] = max(values)
        elif op == "last":
            headline[name] = values[-1]
    return headline


class Runner:
    def __init__(self, labbook):
        self.lb = labbook  # api.Labbook: project_dir, catalog, ledger, cas

    def run(self, ir: dict, param_overrides=None, actor=None) -> dict:
        lb = self.lb
        precheck(ir)
        params = compiler.check_params(ir, param_overrides or {})
        ledger, cas = lb.ledger, lb.cas
        for node in ir["nodes"]:
            for asset in [i["asset"] for i in node.get("inputs") or []] + list(
                node.get("outputs") or []
            ):
                spec = lb.catalog[asset]
                ledger.ensure_asset(asset, spec["kind"], spec["format"])
        run_id = ledger.create_run(
            ir_hash=ir.get("ir_hash") or compiler.ir_hash(ir),
            pipeline_name=ir["pipeline"],
            stack_name=(ir.get("stack") or {}).get("name"),
            code_sha=capture_code_sha(lb.project_dir, ir),
            env_spec=capture_env(),
            params=params,
            actor=actor,
            cache_policy=ir.get("cache_policy"),
        )
        # The lifecycle stamp lands BEFORE any node executes: a killed
        # runner leaves a run in state 'running' with every completed
        # node's materializations already recorded (amnesia test, §3).
        ledger.stamp_lifecycle(run_id, "running")

        producers = {}  # asset -> node name
        for node in ir["nodes"]:
            for asset in node.get("outputs") or []:
                producers[asset] = node["name"]
        node_states = {}  # node name -> set of states across instances
        metrics_so_far = {}
        failed_at = None

        for node in ir["nodes"]:
            name = node["name"]
            instances = self._instances(node)
            for instance, inst_params in instances:
                state = self._run_instance(
                    ir, node, instance, inst_params, run_id, params,
                    producers, node_states, metrics_so_far, failed_at)
                node_states.setdefault(name, set()).add(state)
                if state == "failed" and failed_at is None:
                    failed_at = name
        headline = _aggregate(ir, ledger, run_id)
        if headline:
            ledger.set_headline(run_id, headline)
        ok = failed_at is None and all(
            s <= {"ran", "cached", "skipped-by-gate"}
            for s in node_states.values())
        ledger.stamp_lifecycle(run_id, "completed" if ok else "failed")
        record = ledger.get_run(run_id)
        return {
            "run_id": run_id,
            "lifecycle": record["lifecycle"],
            "ok": ok,
            "headline": headline,
            "nodes": record["nodes"],
        }

    def _instances(self, node):
        fe = node.get("foreach")
        if not fe:
            return [("", {})]
        return [
            (_instance_label(fe, v), {fe["param"]: v}) for v in fe["values"]
        ]

    def _run_instance(self, ir, node, instance, inst_params, run_id, params,
                      producers, node_states, metrics_so_far, failed_at):
        lb = self.lb
        ledger = lb.ledger
        name = node["name"]
        if failed_at is not None:
            ledger.record_node(
                run_id, name, instance, "not-run",
                error=f"not run: upstream node {failed_at!r} failed")
            return "not-run"
        # Producer availability: gated-out or failed inputs propagate as
        # named states, never as missing-data surprises downstream.
        for spec in node.get("inputs") or []:
            asset = spec["asset"]
            producer = producers.get(asset)
            if producer and producer in node_states:
                pstates = node_states[producer]
                if pstates == {"skipped-by-gate"}:
                    ledger.record_node(
                        run_id, name, instance, "skipped-by-gate",
                        gate_expression=node.get("gate"),
                        gate_inputs={"__reason__":
                                     f"input {asset!r} unavailable: producer "
                                     f"{producer!r} was skipped-by-gate"})
                    return "skipped-by-gate"
        # Own gate: condition data over params + metrics logged so far.
        if node.get("gate"):
            names = dict(params)
            names.update(metrics_so_far)
            result, used = gates.evaluate(node["gate"], names)
            if not result:
                ledger.record_node(
                    run_id, name, instance, "skipped-by-gate",
                    gate_expression=node["gate"], gate_inputs=used)
                return "skipped-by-gate"
        # Resolve inputs to materializations.
        input_specs, input_hashes, input_mats = self._resolve_inputs(
            node, run_id)
        # Cache: key = code identity + input hashes + declared params
        # (row 9). Scope is the declared policy, stamped on the run.
        node_params = {p: params[p] for p in node.get("params") or []}
        node_params.update(inst_params)
        cache_key = sha256_bytes(json.dumps({
            "func": node["func"],
            "code": _func_source_hash(node["func"], lb.project_dir),
            "inputs": sorted(input_hashes),
            "params": node_params,
            "outputs": node.get("outputs") or [],
        }, sort_keys=True).encode())
        cached = self._cache_lookup(node, cache_key, run_id, instance)
        if cached is not None:
            ledger.record_node(run_id, name, instance, "cached",
                               cache_key=cache_key,
                               source_run_id=cached["source_run_id"])
            for ev in cached["metrics"]:
                ledger.log_metric(run_id, name, instance, ev["name"],
                                  ev["value"])
                metrics_so_far[ev["name"]] = ev["value"]
            return "cached"
        # Execute in a subprocess.
        started = time.monotonic()
        result = self._execute(node, input_specs, node_params)
        duration_ms = int((time.monotonic() - started) * 1000)
        if result["status"] != "ok":
            ledger.record_node(run_id, name, instance, "failed",
                               error=result.get("error", "node process failed"),
                               duration_ms=duration_ms, cache_key=cache_key)
            return "failed"
        for ev in result["metrics"]:
            ledger.log_metric(run_id, name, instance, ev["name"], ev["value"])
            metrics_so_far[ev["name"]] = ev["value"]
        for asset, spec in result["outputs"].items():
            typed = {}
            if instance:
                k, _, v = instance.partition("=")
                try:
                    typed[k] = int(v)
                except ValueError:
                    typed[k] = v
            if formats.is_pickle_class(spec["format"]):
                typed["pickle_class"] = True  # the flag, in the record (row 2)
            if lb.catalog[asset]["kind"] == "metrics":
                for ev in result["metrics"]:
                    typed[ev["name"]] = ev["value"]
            mid = ledger.record_materialization(
                asset_name=asset, run_id=run_id, node_name=name,
                instance=instance, content_hash=spec["hash"],
                size_bytes=spec["size"], store_path=lb.cas.path(spec["hash"]),
                reader=formats.reader_path(spec["format"]),
                typed_metadata=typed, input_hashes=input_hashes,
                cache_key=cache_key)
            ledger.link_output(run_id, name, instance, asset, mid)
        ledger.record_node(run_id, name, instance, "ran",
                           duration_ms=duration_ms, cache_key=cache_key)
        return "ran"

    def _resolve_inputs(self, node, run_id):
        """Map a node's declared inputs to materializations of this run
        (or ingested external catalog assets). Scalar co-inputs broadcast
        natively: mode 'one' hands the same value to every consumer,
        including every foreach instance (Flyte's fan-out boilerplate is
        refused, row 6)."""
        lb = self.lb
        ledger = lb.ledger
        specs, hashes, mats = {}, [], []
        run = ledger.get_run(run_id)
        outputs = run["outputs"]
        for spec in node.get("inputs") or []:
            asset, mode = spec["asset"], spec["mode"]
            mine = [o for o in outputs if o["asset_name"] == asset]
            if mine:
                chosen = mine if mode == "all" else mine[-1:]
            else:
                chosen = [self._ingest_external(asset, run_id)]
            entries = []
            for o in chosen:
                mat = ledger.materialization_by_id(o["materialization_id"])
                mats.append(mat)
                hashes.append(mat["content_hash"])
                entries.append({"hash": mat["content_hash"],
                                "format": lb.catalog[asset]["format"]})
            specs[asset] = entries if mode == "all" else entries[0]
        return specs, hashes, mats

    def _ingest_external(self, asset, run_id):
        lb = self.lb
        path = lb.catalog.resolve_location(asset, lb.project_dir)
        if path is None or not os.path.exists(path):
            raise LabbookError(
                "external catalog asset has no readable location",
                value={"asset": asset, "location": path},
                expected="a file at the catalog location",
                fix="fix the catalog location or produce the asset upstream",
            )
        with open(path, "rb") as f:
            data = f.read()
        h = lb.cas.put(data)
        spec = lb.catalog[asset]
        mid = lb.ledger.record_materialization(
            asset_name=asset, run_id=run_id, node_name="<catalog>",
            instance="", content_hash=h, size_bytes=len(data),
            store_path=lb.cas.path(h),
            reader=formats.reader_path(spec["format"]),
            typed_metadata={"external": True}, input_hashes=[],
            cache_key=None)
        lb.ledger.link_output(run_id, "<catalog>", "", asset, mid)
        return {"materialization_id": mid}

    def _cache_lookup(self, node, cache_key, run_id, instance):
        lb = self.lb
        ledger = lb.ledger
        outputs = node.get("outputs") or []
        if not outputs:
            return None
        by_run = {}
        for mat in ledger.materializations_by_cache_key(cache_key):
            if mat["run_id"] == run_id:
                continue
            by_run.setdefault(mat["run_id"], []).append(mat)
        for src_run, mats in by_run.items():
            # A cached instance matches on (cache_key, instance): the key
            # already includes the instance params.
            chosen = [m for m in mats if m["instance"] == instance]
            if {m["asset_name"] for m in chosen} >= set(outputs):
                for m in chosen:
                    ledger.link_output(run_id, node["name"], instance,
                                       m["asset_name"],
                                       m["materialization_id"])
                events = [e for e in ledger.metric_events(src_run)
                          if e["node_name"] == node["name"]
                          and e["instance"] == instance]
                return {"source_run_id": src_run, "metrics": events,
                        "materializations": chosen}
        return None

    def _execute(self, node, input_specs, node_params):
        lb = self.lb
        job = {
            "func": node["func"],
            "store": lb.cas.root,
            "inputs": input_specs,
            "output_formats": {
                a: lb.catalog[a]["format"] for a in node.get("outputs") or []
            },
            "params": node_params,
        }
        tmp = tempfile.mkdtemp(prefix="labbook-node-", dir=lb.tmp_dir)
        job_path = os.path.join(tmp, "job.json")
        result_path = os.path.join(tmp, "result.json")
        with open(job_path, "w") as f:
            json.dump(job, f)
        env = dict(os.environ)
        pkg_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env["PYTHONPATH"] = os.pathsep.join(
            [lb.project_dir, pkg_parent, env.get("PYTHONPATH", "")])
        proc = subprocess.run(
            [sys.executable, "-m", "labbook.node_exec", job_path, result_path],
            cwd=lb.project_dir, env=env, capture_output=True, text=True)
        if os.path.exists(result_path):
            with open(result_path) as f:
                return json.load(f)
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return {
            "status": "error",
            "error": "node process died without a result: "
            + (tail[-1] if tail else f"exit {proc.returncode}"),
        }
