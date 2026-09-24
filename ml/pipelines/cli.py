"""cli: python3 -m ml.pipelines.cli <status|run|lanes|cctv>"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from ml.pipelines.contracts.gate import assert_promotable
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lib.engine import run_dag, summarize
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.io import load_json
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.moneyball.explain import explain
from ml.pipelines.moneyball.scorer import score
from ml.pipelines.stages import STAGES
from ml.pipelines.viz.projection import project


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
    }, indent=2))
    return 0


def cmd_run(_: argparse.Namespace) -> int:
    context: dict[str, Any] = {"snapshot": _fixture()}
    results = run_dag(STAGES, context)
    print(json.dumps({"summary": summarize(results), "lanes": context.get("lanes", [])}, indent=2))
    return 0


def cmd_lanes(_: argparse.Namespace) -> int:
    payload = _fixture()
    rows = []
    for pr in payload["prs"]:
        points = score(pr)
        lane = classify_pr(pr)
        rows.append({"number": pr["number"], "lane": lane.value, "score": points, "why": pr.get("why")})
    print(json.dumps(rows, indent=2))
    return 0


def cmd_cctv(_: argparse.Namespace) -> int:
    payload = _fixture()
    lanes = [
        {"number": pr["number"], "lane": classify_pr(pr).value, "score": score(pr), "why": pr.get("why")}
        for pr in payload["prs"]
    ]
    print(json.dumps(project(payload, lanes), indent=2))
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
            lane = classify_pr(pr)
            try:
                assert_promotable(pr, lane)
                print(json.dumps({"number": wanted, "ok": True, "lane": lane.value}))
                return 0
            except GateBlocked as exc:
                print(json.dumps({"number": wanted, "ok": False, "lane": lane.value, "reason": str(exc)}))
                return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ml.pipelines.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("run").set_defaults(func=cmd_run)
    sub.add_parser("lanes").set_defaults(func=cmd_lanes)
    sub.add_parser("cctv").set_defaults(func=cmd_cctv)
    p_ex = sub.add_parser("explain")
    p_ex.add_argument("number", type=int)
    p_ex.set_defaults(func=cmd_explain)
    p_g = sub.add_parser("gate")
    p_g.add_argument("number", type=int)
    p_g.set_defaults(func=cmd_gate)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
