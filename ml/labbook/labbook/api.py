"""The labbook/1 API surface (ledger row 11).

Contract first; this client is *one consumer* of it. The read surface is
deliberately tiny and frozen: run records · per-asset materializations ·
latest-per-asset · compare. All reads are cold-process: no server, ever
(rows 3, 5).
"""

import json
import os
import zipfile

from . import compiler, verify as verify_mod
from .cas import CAS, sha256_bytes
from .catalog import Catalog
from .errors import LabbookError
from .ledger import Ledger
from .runner import Runner


class Labbook:
    def __init__(self, project_dir: str, catalog: Catalog = None):
        self.project_dir = os.path.abspath(project_dir)
        self.state_dir = os.path.join(self.project_dir, ".labbook")
        self.tmp_dir = os.path.join(self.state_dir, "tmp")
        self.ir_dir = os.path.join(self.state_dir, "ir")
        for d in (self.state_dir, self.tmp_dir, self.ir_dir):
            os.makedirs(d, exist_ok=True)
        if catalog is None:
            cat_path = os.path.join(self.project_dir, "catalog.yml")
            catalog = (
                Catalog.load(cat_path)
                if os.path.exists(cat_path)
                else Catalog.from_dict({})
            )
        self.catalog = catalog
        self.ledger = Ledger(os.path.join(self.state_dir, "ledger.db"))
        self.cas = CAS(os.path.join(self.state_dir, "store"))

    def close(self):
        self.ledger.close()

    # ------------------------------------------------------------ compile

    def compile(self, pipeline) -> dict:
        ir = compiler.compile(pipeline, self.catalog)
        self.save_ir(ir)
        return ir

    def save_ir(self, ir: dict):
        path = os.path.join(self.ir_dir, ir["ir_hash"] + ".yml")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(compiler.ir_to_yaml(ir))

    def load_ir(self, ir_hash: str):
        path = os.path.join(self.ir_dir, ir_hash + ".yml")
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return compiler.ir_from_yaml(f.read())

    # ---------------------------------------------------------------- run

    def run(self, ir: dict, params=None, actor=None) -> dict:
        self.save_ir(ir)
        return Runner(self).run(ir, param_overrides=params, actor=actor)

    # --------------------------------------------------------------- reads

    def get_run(self, run_id: str) -> dict:
        return self.ledger.get_run(run_id)

    def materializations(self, asset_name: str):
        return self.ledger.materializations(asset_name)

    def latest(self, asset_name: str):
        return self.ledger.latest(asset_name)

    def compare(self, run_a: str, run_b: str) -> dict:
        """Cross-run comparison as a platform primitive, server-free
        (row 5): param diff · metric diff with computed deltas ·
        artifact-hash diff."""
        la, lb = self.ledger, self.ledger
        ra, rb = la.get_run(run_a), lb.get_run(run_b)
        params = {}
        for k in sorted(set(ra["params"]) | set(rb["params"])):
            va, vb = ra["params"].get(k), rb["params"].get(k)
            params[k] = {"a": va, "b": vb, "changed": va != vb}
        ma, mb = la.run_metric_summary(run_a), lb.run_metric_summary(run_b)
        metrics = {}
        for k in sorted(set(ma) | set(mb)):
            va, vb = ma.get(k), mb.get(k)
            entry = {"a": va, "b": vb}
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                entry["delta"] = vb - va
            metrics[k] = entry
        artifacts = {}
        assets = {m["asset_name"] for m in la.run_materializations(run_a)} | {
            m["asset_name"] for m in lb.run_materializations(run_b)
        }
        for asset in sorted(assets):
            def in_run(ledger, rid):
                mats = [m for m in ledger.run_materializations(rid)
                        if m["asset_name"] == asset]
                return mats[-1]["content_hash"] if mats else None

            ha, hb = in_run(la, run_a), in_run(lb, run_b)
            artifacts[asset] = {"a": ha, "b": hb, "same": ha == hb}
        nodes = {}
        na = {n["node_name"]: n["state"] for n in ra["nodes"]}
        nb = {n["node_name"]: n["state"] for n in rb["nodes"]}
        for k in sorted(set(na) | set(nb)):
            nodes[k] = {"a": na.get(k), "b": nb.get(k)}
        return {"run_a": run_a, "run_b": run_b, "params": params,
                "metrics": metrics, "artifacts": artifacts, "nodes": nodes}

    # ------------------------------------------------------------ promote

    def promote(self, asset_name: str, alias: str, materialization_id: str,
                actor=None):
        """Promotion is an alias: one mutable named pointer over immutable
        versions (row 10), attribution-stamped."""
        return self.ledger.promote(asset_name, alias, materialization_id,
                                   set_by=actor)

    def resolve(self, asset_name: str, alias: str):
        return self.ledger.resolve_alias(asset_name, alias)

    # ------------------------------------------------------------- verify

    def verify(self, run_id: str) -> dict:
        return verify_mod.verify_run(self, run_id)

    # -------------------------------------------------------------- bundle

    def export_bundle(self, run_id: str, out_path: str) -> str:
        """The portable interchange object (§2.2): run record (JSON) +
        metric events (JSONL) + artifacts in native formats + env + IR.
        Self-sufficient: verify from the bundle alone must reproduce the
        headline bit-exactly (ClearML's bar, §3)."""
        record = self.ledger.get_run(run_id)
        mats = self.ledger.run_materializations(run_id)
        for m in mats:
            asset = self.ledger.asset_by_name(m["asset_name"])
            m["format"] = asset["format"]
            m["kind"] = asset["kind"]
        record["materializations"] = mats
        ir = self.load_ir(record["ir_hash"])
        record["ir"] = ir
        events = self.ledger.metric_events(run_id)
        files = {}
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            def add(name, data: bytes):
                z.writestr(name, data)
                files[name] = sha256_bytes(data)

            add("run.json", json.dumps(record, indent=1, sort_keys=True).encode())
            add("metrics.jsonl", "".join(
                json.dumps(e, sort_keys=True) + "\n" for e in events).encode())
            add("ir.yml", compiler.ir_to_yaml(ir).encode() if ir else b"")
            add("env.json", json.dumps(
                {"code_sha": record["code_sha"],
                 "env_spec": json.loads(record["env_spec"])},
                indent=1, sort_keys=True).encode())
            seen = set()
            for m in mats:
                if m["content_hash"] in seen:
                    continue
                seen.add(m["content_hash"])
                add(f"artifacts/{m['content_hash']}",
                    self.cas.get(m["content_hash"]))
            manifest = {"contract": "labbook/1", "run_id": run_id,
                        "files": files}
            z.writestr("manifest.json",
                       json.dumps(manifest, indent=1, sort_keys=True))
        return out_path

    @staticmethod
    def verify_bundle(bundle_path: str) -> dict:
        return verify_mod.verify_bundle(bundle_path)

    # -------------------------------------------------------------- misc

    def catalog_list(self):
        return self.catalog.list()

    def export_pointers(self, out_dir: str):
        return self.ledger.export_pointers(out_dir)


def open_project(project_dir: str) -> Labbook:
    if not os.path.isdir(project_dir):
        raise LabbookError("project directory does not exist",
                           value=project_dir,
                           fix="point labbook at the project root (the "
                           "directory holding catalog.yml)")
    return Labbook(project_dir)
