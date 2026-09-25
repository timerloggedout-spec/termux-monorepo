"""cli: python3 -m ml.pipelines.cli <status|run|lanes|cctv|matrix|explain|gate>"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from ml.pipelines.contracts.gate import assert_promotable, block_reasons
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lib.engine import run_dag, summarize
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.io import load_json
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.moneyball.explain import explain
from ml.pipelines.moneyball.scorer import score
from ml.pipelines.operator.matrix import PRIORITY
from ml.pipelines.stages import STAGES
from ml.pipelines.viz.cctv import emit_cctv
from ml.pipelines.viz.mermaid import dag_mermaid


def _fixture() -> dict[str, Any]:
    return load_json(latest_session_path())


def cmd_status(_: argparse.Namespace) -> int:
    payload = _fixture()
    print(json.dumps({
        "master_sha": payload["master_sha"],
        "issue": 175,
        "open_prs": len(payload["prs"]),
        "operator": "ACTIVE",
        "session": payload.get("session"),
        "fixture": latest_session_path().name,
        "vocab": ["EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"],
    }, indent=2))
    return 0


def cmd_run(_: argparse.Namespace) -> int:
    context: dict[str, Any] = {"snapshot": _fixture()}
    results = run_dag(STAGES, context)
    print(json.dumps({"summary": summarize(results), "lanes": context.get("lanes", []), "counts": context.get("lane_counts")}, indent=2))
    return 0


def cmd_lanes(_: argparse.Namespace) -> int:
    payload = _fixture()
    rows = []
    for pr in payload["prs"]:
        rows.append({"number": pr["number"], "lane": classify_pr(pr).value, "score": score(pr), "why": pr.get("why")})
    print(json.dumps(rows, indent=2))
    return 0


def cmd_cctv(_: argparse.Namespace) -> int:
    print(json.dumps(emit_cctv(_fixture()), indent=2))
    return 0


def cmd_matrix(_: argparse.Namespace) -> int:
    print(json.dumps(PRIORITY, indent=2))
    return 0


def cmd_dag(_: argparse.Namespace) -> int:
    sys.stdout.write(dag_mermaid())
    return 0


def cmd_explain(ns: argparse.Namespace) -> int:
    payload = _fixture()
    wanted = int(ns.number)
    for pr in payload["prs"]:
        if int(pr["number"]) == wanted:
            print(json.dumps(explain(pr), indent=2))
            return 0
    return 1


def cmd_gate(ns: argparse.Namespace) -> int:
    payload = _fixture()
    wanted = int(ns.number)
    for pr in payload["prs"]:
        if int(pr["number"]) == wanted:
            try:
                assert_promotable(pr)
                print(json.dumps({"number": wanted, "promotable": True, "reasons": []}, indent=2))
                return 0
            except GateBlocked as exc:
                print(json.dumps({"number": wanted, "promotable": False, "reasons": exc.reasons}, indent=2))
                return 2
    print(json.dumps({"number": wanted, "reasons": block_reasons({"number": wanted})}, indent=2))
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ml.pipelines")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("run").set_defaults(fn=cmd_run)
    sub.add_parser("lanes").set_defaults(fn=cmd_lanes)
    sub.add_parser("cctv").set_defaults(fn=cmd_cctv)
    sub.add_parser("matrix").set_defaults(fn=cmd_matrix)
    sub.add_parser("dag").set_defaults(fn=cmd_dag)
    explain_p = sub.add_parser("explain")
    explain_p.add_argument("number")
    explain_p.set_defaults(fn=cmd_explain)
    gate_p = sub.add_parser("gate")
    gate_p.add_argument("number")
    gate_p.set_defaults(fn=cmd_gate)
    ns = parser.parse_args(argv)
    return int(ns.fn(ns))


if __name__ == "__main__":
    raise SystemExit(main())
