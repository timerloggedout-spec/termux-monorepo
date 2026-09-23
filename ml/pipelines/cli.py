"""cli: python3 -m ml.pipelines.cli <status|run|lanes>"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .lib.engine import run_dag, summarize
from .lib.io import load_json
from .lib.types import StageStatus
from .moneyball.scorer import classify, score
from .stages.s00_recon.stage import ReconStage
from .stages.s10_ingest.stage import IngestStage
from .stages.s20_features.stage import FeaturesStage
from .stages.s30_train.stage import TrainStage
from .stages.s40_evaluate.stage import EvaluateStage
from .stages.s50_deploy.stage import DeployStage
from .stages.s60_monitor.stage import MonitorStage

STAGES = [
    ("00_recon", ReconStage().run),
    ("10_ingest", IngestStage().run),
    ("20_features", FeaturesStage().run),
    ("30_train", TrainStage().run),
    ("40_evaluate", EvaluateStage().run),
    ("50_deploy", DeployStage().run),
    ("60_monitor", MonitorStage().run),
]


def _fixture() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "fixtures" / "session_20260920.json"
    return load_json(path)


def cmd_status(_: argparse.Namespace) -> int:
    payload = _fixture()
    print(json.dumps({"master_sha": payload["master_sha"], "issue": 175, "open_issues": payload["open_issues"], "open_prs": len(payload["prs"])}, indent=2))
    return 0


def cmd_run(_: argparse.Namespace) -> int:
    context: dict[str, Any] = {"snapshot": _fixture()}
    results = run_dag(STAGES, context)
    print(json.dumps({"summary": summarize(results), "halted": results[-1].status == StageStatus.FAILED}, indent=2))
    return 0 if results and results[-1].status != StageStatus.FAILED else 1


def cmd_lanes(_: argparse.Namespace) -> int:
    payload = _fixture()
    rows = []
    for pr in payload["prs"]:
        points = score(pr)
        rows.append({"number": pr["number"], "lane": classify(points, pr).value, "score": points})
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
