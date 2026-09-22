"""cli: python3 -m ml.pipelines.cli <status|run|lanes>"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, MutableMapping

from .contracts.gate import assert_promotable
from .lib.engine import run_dag, summarize
from .lib.errors import GateBlocked
from .lib.io import load_json
from .lib.types import Lane, StageResult, StageStatus
from .moneyball.scorer import classify, score


def _fixture() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "fixtures" / "session_20260921.json"
    return load_json(path)


def _ok(stage_id: str, **artifacts: Any) -> StageResult:
    return StageResult(stage_id=stage_id, status=StageStatus.OK, artifacts=artifacts)


def stage_recon(ctx: MutableMapping[str, Any]) -> StageResult:
    snap = ctx["snapshot"]
    return _ok("00_recon", master_sha=snap["master_sha"], issue=snap["issue"])


def stage_ingest(ctx: MutableMapping[str, Any]) -> StageResult:
    return _ok("10_ingest", n=len(ctx["snapshot"]["prs"]))


def stage_features(ctx: MutableMapping[str, Any]) -> StageResult:
    scored = [{"number": pr["number"], "score": score(pr)} for pr in ctx["snapshot"]["prs"]]
    ctx["scored"] = scored
    return _ok("20_features", n=len(scored))


def stage_train(ctx: MutableMapping[str, Any]) -> StageResult:
    return _ok("30_train", note="weights static")


def stage_evaluate(ctx: MutableMapping[str, Any]) -> StageResult:
    lanes = [
        {"number": pr["number"], "lane": classify(score(pr), pr).value, "score": score(pr)}
        for pr in ctx["snapshot"]["prs"]
    ]
    ctx["lanes"] = lanes
    return _ok("40_evaluate", lanes=lanes)


def stage_deploy(ctx: MutableMapping[str, Any]) -> StageResult:
    blocked = 0
    for pr in ctx["snapshot"]["prs"]:
        lane = classify(score(pr), pr)
        try:
            assert_promotable(pr, lane)
        except GateBlocked:
            blocked += 1
    return _ok("50_deploy", blocked=blocked)


def stage_monitor(ctx: MutableMapping[str, Any]) -> StageResult:
    return _ok("60_monitor", wait="dual-gate on extract")


STAGES = [
    ("00_recon", stage_recon),
    ("10_ingest", stage_ingest),
    ("20_features", stage_features),
    ("30_train", stage_train),
    ("40_evaluate", stage_evaluate),
    ("50_deploy", stage_deploy),
    ("60_monitor", stage_monitor),
]


def cmd_status(_: argparse.Namespace) -> int:
    payload = _fixture()
    print(json.dumps({"master_sha": payload["master_sha"], "issue": 175, "open_prs": len(payload["prs"])}, indent=2))
    return 0


def cmd_run(_: argparse.Namespace) -> int:
    context: dict[str, Any] = {"snapshot": _fixture()}
    results = run_dag(STAGES, context)
    print(json.dumps({"summary": summarize(results), "lanes": context.get("lanes", [])}, indent=2))
    return 0


def cmd_lanes(_: argparse.Namespace) -> int:
    payload = _fixture()
    rows = [{"number": pr["number"], "lane": classify(score(pr), pr).value, "score": score(pr)} for pr in payload["prs"]]
    print(json.dumps(rows, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ml.pipelines.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("run").set_defaults(func=cmd_run)
    sub.add_parser("lanes").set_defaults(func=cmd_lanes)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
