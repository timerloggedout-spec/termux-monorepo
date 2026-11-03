"""Pipeline declaration + compiler to IR (ledger rows 6, 8, 9).

Pipelines are declared as data: nodes wired by catalog names, with the
graph declared — not hidden in method bodies (Metaflow's do-not-copy #2).
`compile` emits a static, versioned IR (schema `labbook/1`, our own — §4.3
option (b)): components, typed edges, parameters with types + defaults,
gates as condition *data* over named outputs, and the cache policy
declared in the definition — never a compiler default (Kubeflow row 9).
"""

import hashlib
import json

from . import yamlmini
from .errors import LabbookError

IR_SCHEMA = "labbook/1"
PARAM_TYPES = ("int", "float", "str", "bool")
NODE_KINDS = ("python",)  # v1 executes exactly this; anything else is
# refused by name at compile-check/run precheck (row 6).


class Node:
    def __init__(self, name, func, inputs=None, outputs=None, params=None,
                 foreach=None, gate=None, kind="python"):
        self.name = name
        self.func = func  # "module:attr" — the code identity of the node
        self.inputs = inputs or {}  # {asset_name: "one"|"all"}
        self.outputs = outputs or []  # [asset_name]
        self.params = params or []  # pipeline param names this node consumes
        self.foreach = foreach  # {"param": name, "values": [...]} or None
        self.gate = gate  # condition string over named outputs, or None
        self.kind = kind

    def to_ir(self):
        return {
            "name": self.name,
            "func": self.func,
            "kind": self.kind,
            "inputs": [
                {"asset": a, "mode": m} for a, m in self.inputs.items()
            ],
            "outputs": list(self.outputs),
            "params": list(self.params),
            "foreach": self.foreach,
            "gate": self.gate,
        }


class Pipeline:
    def __init__(self, name, nodes, params=None, cache_policy=None,
                 stack_name="local", aggregates=None, verify=None):
        self.name = name
        self.nodes = nodes
        self.params = params or {}  # {name: {"type":..., "default":...}}
        self.cache_policy = cache_policy
        self.stack_name = stack_name
        self.aggregates = aggregates or {}
        self.verify = verify  # verify strategy spec (§3 round-trip), or None


def compile(pipeline: Pipeline, catalog) -> dict:
    """Validate a declared pipeline against the catalog and emit IR."""
    if pipeline.cache_policy is None:
        raise LabbookError(
            "pipeline declares no cache policy",
            value=pipeline.name,
            expected="an explicit cache_policy in the pipeline definition",
            fix="declare it (e.g. 'per-artifact-store'); cache semantics "
            "are never a compiler default (row 9)",
        )
    for pname, pspec in pipeline.params.items():
        if pspec.get("type") not in PARAM_TYPES:
            raise LabbookError(
                "param has an unknown type",
                value={"param": pname, "type": pspec.get("type")},
                expected=f"one of {PARAM_TYPES}",
            )
    produced = {}  # asset -> producing node name
    seen_nodes = set()
    for node in pipeline.nodes:
        if node.name in seen_nodes:
            raise LabbookError("duplicate node name", value=node.name)
        seen_nodes.add(node.name)
        if node.kind not in NODE_KINDS:
            raise LabbookError(
                "node kind is not executable in this contract version",
                value={"node": node.name, "kind": node.kind},
                expected=f"one of {NODE_KINDS} for labbook/1",
                fix="the runner refuses constructs by name rather than "
                "silently dropping them (row 6)",
            )
        for asset in list(node.inputs) + list(node.outputs):
            if asset not in catalog:
                raise LabbookError(
                    "node references an asset outside the catalog",
                    value={"node": node.name, "asset": asset},
                    expected="every input/output is a catalog asset (row 8)",
                )
        for asset, mode in node.inputs.items():
            if mode not in ("one", "all"):
                raise LabbookError(
                    "input mode is unknown",
                    value={"node": node.name, "asset": asset, "mode": mode},
                    expected="'one' (single materialization) or 'all' "
                    "(every materialization produced in this run — joins)",
                )
            if asset not in produced and not catalog[asset].get("location"):
                raise LabbookError(
                    "input is neither produced upstream nor an external "
                    "catalog asset",
                    value={"node": node.name, "asset": asset},
                    expected="an earlier node outputs it, or the catalog "
                    "gives it a location",
                )
        for pname in node.params:
            if pname not in pipeline.params:
                raise LabbookError(
                    "node consumes an undeclared param",
                    value={"node": node.name, "param": pname},
                    expected="params are declared on the pipeline with "
                    "types + defaults",
                )
        if node.foreach is not None:
            if not node.foreach.get("values"):
                raise LabbookError(
                    "foreach declares no values",
                    value={"node": node.name},
                    expected="a non-empty values list",
                )
        for asset in node.outputs:
            if asset in produced:
                raise LabbookError(
                    "asset is produced by two nodes",
                    value={"asset": asset,
                          "nodes": [produced[asset], node.name]},
                    expected="one producer per asset per pipeline "
                    "(instances of one foreach node excepted)",
                )
            produced[asset] = node.name
    for agg_name, agg in pipeline.aggregates.items():
        if agg.get("op") not in ("mean", "sum", "min", "max", "last"):
            raise LabbookError(
                "aggregate has an unknown op",
                value={"aggregate": agg_name, "op": agg.get("op")},
                expected="one of mean/sum/min/max/last",
            )
    ir = {
        "schemaVersion": IR_SCHEMA,
        "pipeline": pipeline.name,
        "stack": {"name": pipeline.stack_name},
        "cache_policy": pipeline.cache_policy,
        "params": pipeline.params,
        "nodes": [n.to_ir() for n in pipeline.nodes],
        "aggregates": pipeline.aggregates,
        "verify": pipeline.verify,
    }
    ir["ir_hash"] = ir_hash(ir)
    return ir


def ir_hash(ir: dict) -> str:
    body = {k: v for k, v in ir.items() if k != "ir_hash"}
    canon = json.dumps(body, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()


def ir_to_yaml(ir: dict) -> str:
    return yamlmini.dump(ir)


def ir_from_yaml(text: str) -> dict:
    ir = yamlmini.load(text)
    if not isinstance(ir, dict) or ir.get("schemaVersion") != IR_SCHEMA:
        raise LabbookError(
            "not a labbook/1 IR document",
            value=(ir or {}).get("schemaVersion"),
            expected=IR_SCHEMA,
            fix="compile the pipeline with this version of labbook",
        )
    return ir


def check_params(ir: dict, overrides: dict) -> dict:
    """Merge param overrides over declared defaults, enforcing the
    declared types (write-once, typed — §2.2)."""
    merged = {}
    declared = ir.get("params") or {}
    for name, spec in declared.items():
        merged[name] = spec.get("default")
    for name, value in (overrides or {}).items():
        if name not in declared:
            raise LabbookError(
                "run overrides an undeclared param",
                value=name,
                expected=f"one of {sorted(declared)}",
            )
        merged[name] = value
    for name, spec in declared.items():
        v = merged[name]
        if v is None:
            continue
        t = spec["type"]
        ok = (
            (t == "int" and isinstance(v, int) and not isinstance(v, bool))
            or (t == "float" and isinstance(v, (int, float)) and not isinstance(v, bool))
            or (t == "str" and isinstance(v, str))
            or (t == "bool" and isinstance(v, bool))
        )
        if not ok:
            raise LabbookError(
                "param value does not match its declared type",
                value={"param": name, "value": v},
                expected=f"type {t}",
            )
        if t == "float":
            merged[name] = float(v)
    return merged
