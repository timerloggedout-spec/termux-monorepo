"""Verify (ledger rows 2, 6, 12; §3 validation plan).

`verify` re-derives headline results from stored parts and reports
PASS/FAIL *per check, named* — written to be consumed as rule-9 evidence
(DoE truth bar), not as a green checkmark. A check that cannot be
performed is a FAIL naming why, never a skip.

The fold-MSE strategy is the program's canonical round trip (the check
Metaflow, ClearML, ZenML, Dagster, DVC, MLRun and Kubeflow were all held
to): recompute each fold's MSE from the stored dataset artifact + the
stored model artifacts, in stored order, and require exact agreement
with both the recorded per-fold metric events and the stamped headline.
"""

import json
import os
import tempfile
import zipfile

from . import formats
from .cas import sha256_bytes
from .errors import LabbookError


def _feature_value(name, row):
    if name == "1":
        return 1.0
    if name in row:
        return float(row[name])
    if name.endswith("^2") and name[:-2] in row:
        x = float(row[name[:-2]])
        return x * x
    raise LabbookError("verify cannot evaluate feature", value=name,
                       expected="a dataset column, '1', or '<col>^2'")


def fold_mses(dataset_rows, models):
    """Recompute per-fold MSEs. models: [{fold, features, coef}] ordered
    by fold. Fold of row i is i % n_folds — the demo's declared split.
    Arithmetic mirrors the producing nodes exactly (row order, sum then
    divide) so agreement is bit-exact, not approximate."""
    n_folds = len(models)
    out = []
    for model in sorted(models, key=lambda m: m["fold"]):
        fold = model["fold"]
        rows = [r for i, r in enumerate(dataset_rows) if i % n_folds == fold]
        se = 0.0
        for r in rows:
            pred = 0.0
            for coef, feat in zip(model["coef"], model["features"]):
                pred += coef * _feature_value(feat, r)
            se += (float(r["y"]) - pred) ** 2
        out.append(se / len(rows))
    return out


def _check(name, ok, detail):
    return {"check": name, "pass": bool(ok), "detail": detail}


def verify_fold_strategy(*, spec, get_artifact, metric_events, headline,
                         metrics_typed):
    """Shared by run-verify and bundle-verify. get_artifact(asset) ->
    [(typed_metadata, value)] for the run's materializations of asset."""
    checks = []
    try:
        dataset = get_artifact(spec["dataset"])
        if not dataset:
            return [_check("headline-recompute", False,
                           f"no materialization of dataset "
                           f"{spec['dataset']!r}")]
        dataset_rows = dataset[0][1]
        models = []
        for typed, value in get_artifact(spec["models"]):
            if "fold" not in typed:
                return [_check("headline-recompute", False,
                               "model materialization lacks a fold stamp")]
            models.append({"fold": typed["fold"],
                           "features": value["features"],
                           "coef": value["coef"]})
        recomputed = fold_mses(dataset_rows, models)
    except Exception as e:  # noqa: BLE001 — a corrupt part is a FAIL, named
        return [_check("headline-recompute", False,
                       f"stored parts unreadable: {type(e).__name__}: {e}")]
    events = [e["value"] for e in metric_events
              if e["name"] == spec["metric"]]
    if events != recomputed:
        checks.append(_check(
            "fold-metrics-match-stored-parts", False,
            f"recorded fold metrics {events} != recomputed {recomputed}"))
    else:
        checks.append(_check(
            "fold-metrics-match-stored-parts", True,
            f"{len(events)} fold metrics reproduced exactly"))
    mean = sum(recomputed) / len(recomputed)
    head = headline.get(spec["headline"])
    checks.append(_check(
        "headline-recompute", head == mean,
        f"headline {spec['headline']}={head!r} recomputed={mean!r}"))
    if metrics_typed is not None:
        stamped = metrics_typed.get(spec["headline"])
        checks.append(_check(
            "metrics-asset-headline", stamped == mean,
            f"metrics asset stamped {stamped!r} recomputed={mean!r}"))
    return checks


def verify_run(lb, run_id):
    """Cold-process verification of a recorded run against the ledger +
    CAS. Every materialization hash-verifies; declared formats and the
    pickle-class flag are checked; the headline is re-derived."""
    ledger = lb.ledger
    record = ledger.get_run(run_id)
    checks = []
    mats = ledger.run_materializations(run_id)
    bad = []
    for m in mats:
        try:
            lb.cas.get(m["content_hash"])
        except LabbookError as e:
            bad.append(f"{m['asset_name']}:{m['content_hash'][:8]} ({e})")
    checks.append(_check(
        "artifact-hashes-verify", not bad,
        f"{len(mats)} materializations hash-verified"
        + (f"; failures: {bad}" if bad else "")))
    undeclared, unflagged = [], []
    for m in mats:
        asset = ledger.asset_by_name(m["asset_name"])
        if not asset or not asset["format"]:
            undeclared.append(m["asset_name"])
        if formats.is_pickle_class(asset["format"]) and not m[
            "typed_metadata"
        ].get("pickle_class"):
            unflagged.append(m["asset_name"])
    checks.append(_check(
        "formats-declared", not undeclared,
        "every artifact carries a declared format"
        + (f"; undeclared: {undeclared}" if undeclared else "")))
    checks.append(_check(
        "pickle-class-flagged", not unflagged,
        "pickle-class artifacts are flagged in the record"
        + (f"; unflagged: {unflagged}" if unflagged else "")))
    ir = lb.load_ir(record["ir_hash"])
    if ir is None:
        checks.append(_check("ir-present", False,
                             f"IR {record['ir_hash'][:12]} not in the "
                             "project's IR store"))
    else:
        checks.append(_check("ir-present", True,
                             f"IR {record['ir_hash'][:12]} present"))
        ir_nodes = {n["name"] for n in ir.get("nodes") or []}
        recorded = {n["node_name"] for n in record["nodes"]}
        missing = ir_nodes - recorded
        checks.append(_check(
            "node-enumeration", not missing,
            "verdict enumerates every IR node"
            + (f"; MISSING BY NAME: {sorted(missing)}" if missing else "")))
        spec = ir.get("verify")
        if spec:
            def get_artifact(asset):
                out = []
                for m in ledger.run_materializations(run_id):
                    if m["asset_name"] == asset:
                        value = formats.read(
                            ledger.asset_by_name(asset)["format"],
                            lb.cas.get(m["content_hash"]))
                        out.append((m["typed_metadata"], value))
                return out

            metrics_typed = None
            for m in mats:
                if ledger.asset_by_name(m["asset_name"])["kind"] == "metrics":
                    metrics_typed = m["typed_metadata"]
            checks.extend(verify_fold_strategy(
                spec=spec, get_artifact=get_artifact,
                metric_events=ledger.metric_events(run_id),
                headline=record["headline"], metrics_typed=metrics_typed))
    return {"run_id": run_id, "pass": all(c["pass"] for c in checks),
            "checks": checks}


def verify_bundle(bundle_path):
    """Bundle self-sufficiency (§3): verify from the zip alone, on a
    machine with nothing else. No ledger, no CAS — the bundle's own
    records and bytes must reproduce the headline bit-exactly or name
    the failed check."""
    checks = []
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(bundle_path) as z:
            names = set(z.namelist())
            z.extractall(td)

        def load(name):
            with open(os.path.join(td, name), "rb") as f:
                return f.read()

        manifest = json.loads(load("manifest.json"))
        run = json.loads(load("run.json"))
        bad = []
        for fname, want in manifest["files"].items():
            if sha256_bytes(load(fname)) != want:
                bad.append(fname)
        checks.append(_check(
            "bundle-manifest", not bad,
            "every bundled file matches the manifest"
            + (f"; mismatched: {bad}" if bad else "")))
        artifacts = {}
        for m in run["materializations"]:
            rel = f"artifacts/{m['content_hash']}"
            if rel not in names:
                bad.append(rel)
                continue
            data = load(rel)
            if sha256_bytes(data) != m["content_hash"]:
                bad.append(rel + " (hash)")
            artifacts.setdefault(m["asset_name"], []).append(
                (m["typed_metadata"], data, m["format"]))
        checks.append(_check(
            "bundle-artifact-hashes", not bad,
            f"{sum(len(v) for v in artifacts.values())} artifacts present "
            "and hash-true" + (f"; problems: {bad}" if bad else "")))
        unflagged = [
            m["asset_name"] for m in run["materializations"]
            if formats.is_pickle_class(m["format"])
            and not m["typed_metadata"].get("pickle_class")
        ]
        checks.append(_check(
            "pickle-class-flagged", not unflagged,
            "pickle-class artifacts flagged in the bundle record"
            + (f"; unflagged: {unflagged}" if unflagged else "")))
        ir = run.get("ir") or {}
        spec = ir.get("verify")
        if spec:
            def get_artifact(asset):
                return [
                    (typed, formats.read(fmt, data))
                    for typed, data, fmt in artifacts.get(asset, [])
                ]

            events = [
                json.loads(line)
                for line in load("metrics.jsonl").decode().splitlines()
                if line.strip()
            ]
            metrics_typed = None
            for m in run["materializations"]:
                if m["kind"] == "metrics":
                    metrics_typed = m["typed_metadata"]
            checks.extend(verify_fold_strategy(
                spec=spec, get_artifact=get_artifact,
                metric_events=events, headline=run["headline"],
                metrics_typed=metrics_typed))
    return {"bundle": os.path.basename(bundle_path),
            "pass": all(c["pass"] for c in checks), "checks": checks}
