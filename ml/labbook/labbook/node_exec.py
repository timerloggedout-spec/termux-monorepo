"""Node execution subprocess entry: `python -m labbook.node_exec job.json`.

The runner executes every node in a subprocess (execution model §2.5 —
Kubeflow's SubprocessRunner proved the unconditional DAG runs fine this
way), so a node crash is a process exit, not a corrupted runner. The job
spec carries content hashes, never paths into another run's internals;
inputs are loaded from the CAS through their declared formats, outputs
are written back the same way.

Contract:
  job.json in : {func, store, inputs: {asset: {hash, format} |
                 [{hash, format}, ...]}, params, instance}
  node func   : fn(ctx, inputs, params) -> {asset_name: value}
                ctx.log_metric(name, value) records a metric event
  result.json : {status: ok, outputs: {asset: {hash, format, size}},
                 metrics: [{name, value}]}
                or {status: error, error: "ClassName: message",
                 traceback: ...} — the single primary exception, verbatim
                 (row 7). Nothing is swallowed.
"""

import importlib
import json
import sys
import traceback

from . import formats
from .cas import CAS


class Ctx:
    def __init__(self):
        self.metrics = []

    def log_metric(self, name, value):
        self.metrics.append({"name": name, "value": float(value)})


def main(argv):
    with open(argv[1]) as f:
        job = json.load(f)
    cas = CAS(job["store"])
    result_path = argv[2]
    try:
        inputs = {}
        for asset, spec in job["inputs"].items():
            if isinstance(spec, list):
                inputs[asset] = [
                    formats.read(s["format"], cas.get(s["hash"])) for s in spec
                ]
            else:
                inputs[asset] = formats.read(spec["format"], cas.get(spec["hash"]))
        module_name, attr = job["func"].split(":")
        fn = getattr(importlib.import_module(module_name), attr)
        ctx = Ctx()
        outputs = fn(ctx, inputs, job["params"]) or {}
        out_spec = {}
        for asset, fmt in job["output_formats"].items():
            if asset not in outputs:
                raise KeyError(
                    f"node did not produce declared output {asset!r}; "
                    f"produced: {sorted(outputs)}"
                )
            data = formats.write(fmt, outputs[asset])
            h = cas.put(data)
            out_spec[asset] = {"hash": h, "format": fmt, "size": len(data)}
        result = {"status": "ok", "outputs": out_spec, "metrics": ctx.metrics}
    except BaseException as e:  # noqa: BLE001 — the record must carry it
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }
    with open(result_path, "w") as f:
        json.dump(result, f)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
