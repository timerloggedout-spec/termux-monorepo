"""The ledger (ledger rows 3, 4, 13).

One SQLite database, append-only event tables, behind the API. Runs,
node runs, assets, materializations, metric events, promotions — all
readable from a cold process with nothing running (Dagster's local
instance is the proof this shape serves a lab; Flyte's local amnesia and
MLRun's silent NopDB are the refused alternatives).

Mutability follows MLflow's three-way split: params write-once, metrics
append-only, tags/promotions append-only events. The run row's lifecycle
fields are stamped at every transition (row 13) — in the record itself,
never inferable only from a server's view.
"""

import json
import os
import sqlite3
import time
import uuid

from .errors import LabbookError

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  ir_hash TEXT NOT NULL,
  pipeline_name TEXT NOT NULL,
  stack_name TEXT,
  lifecycle TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  code_sha TEXT NOT NULL,
  env_spec TEXT NOT NULL,
  params_json TEXT NOT NULL,
  actor TEXT,
  cache_policy TEXT,
  headline_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS node_runs (
  run_id TEXT NOT NULL,
  node_name TEXT NOT NULL,
  instance TEXT NOT NULL DEFAULT '',
  state TEXT NOT NULL,
  gate_expression TEXT,
  gate_inputs_json TEXT,
  error TEXT,
  duration_ms INTEGER,
  cache_key TEXT,
  source_run_id TEXT,
  PRIMARY KEY (run_id, node_name, instance)
);
CREATE TABLE IF NOT EXISTS assets (
  asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  kind TEXT NOT NULL,
  format TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS materializations (
  materialization_id TEXT PRIMARY KEY,
  asset_id INTEGER NOT NULL,
  run_id TEXT NOT NULL,
  node_name TEXT NOT NULL,
  instance TEXT NOT NULL DEFAULT '',
  content_hash TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  store_path TEXT NOT NULL,
  reader TEXT NOT NULL,
  typed_metadata_json TEXT NOT NULL DEFAULT '{}',
  input_hashes_json TEXT NOT NULL DEFAULT '[]',
  cache_key TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mat_cache ON materializations(cache_key);
CREATE INDEX IF NOT EXISTS idx_mat_asset ON materializations(asset_id, created_at);
CREATE TABLE IF NOT EXISTS run_outputs (
  run_id TEXT NOT NULL,
  node_name TEXT NOT NULL,
  instance TEXT NOT NULL DEFAULT '',
  asset_name TEXT NOT NULL,
  materialization_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metric_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  asset_name TEXT,
  node_name TEXT NOT NULL,
  instance TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL,
  value REAL NOT NULL,
  step INTEGER,
  at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS promotions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_name TEXT NOT NULL,
  alias TEXT NOT NULL,
  materialization_id TEXT NOT NULL,
  set_by TEXT,
  set_at TEXT NOT NULL
);
"""

NODE_STATES = ("ran", "cached", "skipped-by-gate", "failed", "not-supported", "not-run")
LIFECYCLES = ("created", "running", "completed", "failed")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Ledger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ------------------------------------------------------------- runs

    def create_run(self, *, ir_hash, pipeline_name, stack_name, code_sha,
                   env_spec, params, actor, cache_policy) -> str:
        run_id = uuid.uuid4().hex
        self.conn.execute(
            "INSERT INTO runs (run_id, ir_hash, pipeline_name, stack_name,"
            " lifecycle, code_sha, env_spec, params_json, actor, cache_policy)"
            " VALUES (?,?,?,?, 'created', ?,?,?,?,?)",
            (run_id, ir_hash, pipeline_name, stack_name, code_sha, env_spec,
             json.dumps(params, sort_keys=True), actor, cache_policy),
        )
        self.conn.commit()
        return run_id

    def stamp_lifecycle(self, run_id: str, lifecycle: str):
        if lifecycle not in LIFECYCLES:
            raise LabbookError("unknown lifecycle state", value=lifecycle,
                               expected=f"one of {LIFECYCLES}")
        if lifecycle == "running":
            self.conn.execute(
                "UPDATE runs SET lifecycle='running', started_at=? WHERE run_id=?",
                (now_iso(), run_id))
        elif lifecycle in ("completed", "failed"):
            self.conn.execute(
                "UPDATE runs SET lifecycle=?, finished_at=? WHERE run_id=?",
                (lifecycle, now_iso(), run_id))
        else:
            self.conn.execute(
                "UPDATE runs SET lifecycle=? WHERE run_id=?", (lifecycle, run_id))
        self.conn.commit()

    def set_headline(self, run_id: str, headline: dict):
        self.conn.execute(
            "UPDATE runs SET headline_json=? WHERE run_id=?",
            (json.dumps(headline, sort_keys=True), run_id))
        self.conn.commit()

    def get_run(self, run_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise LabbookError("no such run", value=run_id,
                               expected="a run_id recorded in the ledger",
                               fix="check the id, or list runs via the ledger")
        run = dict(row)
        run["params"] = json.loads(run.pop("params_json"))
        run["headline"] = json.loads(run.pop("headline_json"))
        nodes = self.conn.execute(
            "SELECT * FROM node_runs WHERE run_id=? ORDER BY rowid",
            (run_id,)).fetchall()
        run["nodes"] = []
        for n in nodes:
            nd = dict(n)
            if nd.get("gate_inputs_json"):
                nd["gate_inputs"] = json.loads(nd.pop("gate_inputs_json"))
            else:
                nd.pop("gate_inputs_json", None)
                nd["gate_inputs"] = None
            run["nodes"].append(nd)
        outs = self.conn.execute(
            "SELECT * FROM run_outputs WHERE run_id=? ORDER BY rowid",
            (run_id,)).fetchall()
        run["outputs"] = [dict(o) for o in outs]
        return run

    def record_node(self, run_id, node_name, instance, state, *,
                    gate_expression=None, gate_inputs=None, error=None,
                    duration_ms=None, cache_key=None, source_run_id=None):
        if state not in NODE_STATES:
            raise LabbookError("unknown node state", value=state,
                               expected=f"one of {NODE_STATES}")
        self.conn.execute(
            "INSERT OR REPLACE INTO node_runs (run_id, node_name, instance,"
            " state, gate_expression, gate_inputs_json, error, duration_ms,"
            " cache_key, source_run_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (run_id, node_name, instance, state, gate_expression,
             json.dumps(gate_inputs, sort_keys=True) if gate_inputs is not None else None,
             error, duration_ms, cache_key, source_run_id))
        self.conn.commit()

    # ------------------------------------------------------------- assets

    def ensure_asset(self, name, kind, fmt) -> int:
        row = self.conn.execute(
            "SELECT asset_id, kind, format FROM assets WHERE name=?",
            (name,)).fetchone()
        if row is not None:
            if row["kind"] != kind or row["format"] != fmt:
                raise LabbookError(
                    "asset redeclared with a different kind/format",
                    value={"name": name, "kind": kind, "format": fmt},
                    expected=f"kind={row['kind']} format={row['format']} "
                    "(an asset's declared format is part of its identity)",
                    fix="rename the asset or change the catalog deliberately",
                )
            return row["asset_id"]
        cur = self.conn.execute(
            "INSERT INTO assets (name, kind, format) VALUES (?,?,?)",
            (name, kind, fmt))
        self.conn.commit()
        return cur.lastrowid

    def asset_by_name(self, name):
        row = self.conn.execute(
            "SELECT * FROM assets WHERE name=?", (name,)).fetchone()
        return dict(row) if row else None

    # --------------------------------------------------- materializations

    def record_materialization(self, *, asset_name, run_id, node_name,
                                 instance, content_hash, size_bytes,
                                 store_path, reader, typed_metadata,
                                 input_hashes, cache_key) -> str:
        asset = self.asset_by_name(asset_name)
        if asset is None:
            raise LabbookError("materialization for unknown asset",
                               value=asset_name,
                               expected="asset declared via ensure_asset first")
        mid = uuid.uuid4().hex
        self.conn.execute(
            "INSERT INTO materializations (materialization_id, asset_id,"
            " run_id, node_name, instance, content_hash, size_bytes,"
            " store_path, reader, typed_metadata_json, input_hashes_json,"
            " cache_key, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (mid, asset["asset_id"], run_id, node_name, instance,
             content_hash, size_bytes, store_path, reader,
             json.dumps(typed_metadata, sort_keys=True),
             json.dumps(list(input_hashes)), cache_key, now_iso()))
        self.conn.commit()
        return mid

    def link_output(self, run_id, node_name, instance, asset_name,
                    materialization_id):
        self.conn.execute(
            "INSERT INTO run_outputs (run_id, node_name, instance,"
            " asset_name, materialization_id) VALUES (?,?,?,?,?)",
            (run_id, node_name, instance, asset_name, materialization_id))
        self.conn.commit()

    def _mat_dict(self, row) -> dict:
        d = dict(row)
        d["typed_metadata"] = json.loads(d.pop("typed_metadata_json"))
        d["input_hashes"] = json.loads(d.pop("input_hashes_json"))
        return d

    def materializations(self, asset_name, run_id=None):
        asset = self.asset_by_name(asset_name)
        if asset is None:
            return []
        q = ("SELECT m.*, a.name AS asset_name FROM materializations m"
             " JOIN assets a ON a.asset_id = m.asset_id"
             " WHERE m.asset_id=?")
        args = [asset["asset_id"]]
        if run_id is not None:
            q += " AND m.run_id=?"
            args.append(run_id)
        q += " ORDER BY m.created_at DESC, m.rowid DESC"
        return [self._mat_dict(r) for r in self.conn.execute(q, args)]

    def latest(self, asset_name):
        mats = self.materializations(asset_name)
        return mats[0] if mats else None

    def materialization_by_id(self, materialization_id):
        row = self.conn.execute(
            "SELECT m.*, a.name AS asset_name FROM materializations m"
            " JOIN assets a ON a.asset_id = m.asset_id"
            " WHERE m.materialization_id=?", (materialization_id,)).fetchone()
        return self._mat_dict(row) if row else None

    def materializations_by_cache_key(self, cache_key):
        rows = self.conn.execute(
            "SELECT m.*, a.name AS asset_name FROM materializations m"
            " JOIN assets a ON a.asset_id = m.asset_id"
            " WHERE m.cache_key=? ORDER BY m.created_at", (cache_key,)).fetchall()
        return [self._mat_dict(r) for r in rows]

    def run_materializations(self, run_id):
        """The run's output set: materializations linked via run_outputs,
        whether this run produced them or reused them from cache (the
        materialization's own run_id stays the *origin* run — both facts
        are in the record)."""
        rows = self.conn.execute(
            "SELECT m.*, a.name AS asset_name FROM run_outputs o"
            " JOIN materializations m"
            "   ON m.materialization_id = o.materialization_id"
            " JOIN assets a ON a.asset_id = m.asset_id"
            " WHERE o.run_id=? ORDER BY o.rowid", (run_id,)).fetchall()
        seen, out = set(), []
        for r in rows:
            d = self._mat_dict(r)
            if d["materialization_id"] in seen:
                continue
            seen.add(d["materialization_id"])
            d["produced_by_this_run"] = d["run_id"] == run_id
            out.append(d)
        return out

    # ------------------------------------------------------------- metrics

    def log_metric(self, run_id, node_name, instance, name, value,
                   asset_name=None, step=None):
        """Append-only metric event. The name is the name — no magic
        'Summary', no sentinel iterations (ClearML row 7, refused)."""
        self.conn.execute(
            "INSERT INTO metric_events (run_id, asset_name, node_name,"
            " instance, name, value, step, at) VALUES (?,?,?,?,?,?,?,?)",
            (run_id, asset_name, node_name, instance, name, float(value),
             step, now_iso()))
        self.conn.commit()

    def metric_events(self, run_id, name=None, node_name=None):
        q = "SELECT * FROM metric_events WHERE run_id=?"
        args = [run_id]
        if name is not None:
            q += " AND name=?"
            args.append(name)
        if node_name is not None:
            q += " AND node_name=?"
            args.append(node_name)
        q += " ORDER BY id"
        return [dict(r) for r in self.conn.execute(q, args)]

    def run_metric_summary(self, run_id):
        """{metric_name: last value} over a run's events, plus the run's
        stamped headline — the comparison currency (row 5)."""
        out = {}
        for ev in self.metric_events(run_id):
            out[ev["name"]] = ev["value"]
        run = self.get_run(run_id)
        for k, v in run["headline"].items():
            out.setdefault(k, v)
        return out

    # ---------------------------------------------------------- promotions

    def promote(self, asset_name, alias, materialization_id, set_by):
        mat = self.materialization_by_id(materialization_id)
        if mat is None:
            raise LabbookError("promotion target does not exist",
                               value=materialization_id,
                               expected="a materialization_id in the ledger")
        if mat["asset_name"] != asset_name:
            raise LabbookError(
                "promotion target belongs to another asset",
                value={"asset": asset_name, "materialization_of": mat["asset_name"]},
                expected="materialization of the named asset")
        self.conn.execute(
            "INSERT INTO promotions (asset_name, alias, materialization_id,"
            " set_by, set_at) VALUES (?,?,?,?,?)",
            (asset_name, alias, materialization_id, set_by, now_iso()))
        self.conn.commit()
        return self.resolve_alias(asset_name, alias)

    def resolve_alias(self, asset_name, alias):
        row = self.conn.execute(
            "SELECT * FROM promotions WHERE asset_name=? AND alias=?"
            " ORDER BY id DESC LIMIT 1", (asset_name, alias)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["materialization"] = self.materialization_by_id(d["materialization_id"])
        return d

    # ------------------------------------------------------------ pointers

    def export_pointers(self, out_dir):
        """Git pointer records (row 1): small, diffable JSON files naming
        hash + size + format + reader. Bytes stay in the CAS."""
        os.makedirs(out_dir, exist_ok=True)
        written = []
        rows = self.conn.execute(
            "SELECT m.*, a.name AS asset_name, a.format AS fmt FROM"
            " materializations m JOIN assets a ON a.asset_id = m.asset_id"
            " ORDER BY m.created_at").fetchall()
        for r in rows:
            d = self._mat_dict(r)
            ptr = {
                "asset": d["asset_name"],
                "materialization_id": d["materialization_id"],
                "content_hash": d["content_hash"],
                "size_bytes": d["size_bytes"],
                "format": d["fmt"],
                "reader": d["reader"],
                "run_id": d["run_id"],
                "node": d["node_name"],
                "instance": d["instance"],
                "created_at": d["created_at"],
            }
            path = os.path.join(
                out_dir, d["asset_name"].replace("/", "_"),
                d["materialization_id"] + ".json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(ptr, f, indent=2, sort_keys=True)
            written.append(path)
        return written
