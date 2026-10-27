"""Dispatch — run one observatory trial from the command line.

Entry point for .github/workflows/classifier-trial-dispatch.yml
(workflow_dispatch). Reads no credentials itself: adapters read their
provider keys from the environment and trial.py reads the HindSight env.

Free-only policy (owner rule): by default only approved free routes may
run — the gemini free tier and OpenRouter free models. --allow-paid is
the explicit escape hatch and is owner-gated at the workflow layer.

Exit code is non-zero when the policy refuses a route or when the trial
produced no winning artifact, so a green workflow run means a real trial
executed end to end (Mev -> Jev -> Kev -> Laya).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .trial import run_trial

FREE_PROVIDERS = {"gemini", "openrouter"}
DEFAULT_RUBRIC = {
    "quality": "0..1 overall quality of the response",
    "grounding": "0..1 factual grounding; penalize fabrication",
}


def parse_endpoint(spec: str) -> tuple[str, str]:
    prov, sep, model = spec.partition(":")
    if not sep or not prov or not model:
        raise ValueError(f"endpoint must be prov:model, got {spec!r}")
    return prov, model


def assert_free_only(providers: list, judge: tuple, allow_paid: bool) -> None:
    if allow_paid:
        return
    for prov, model in list(providers) + [judge]:
        if prov not in FREE_PROVIDERS:
            raise SystemExit(
                f"free_only: provider {prov!r} is not an approved free route "
                f"(allowed: {sorted(FREE_PROVIDERS)}); use --allow-paid only "
                "with explicit owner approval")
        if prov == "openrouter" and not (
                model == "openrouter/free" or model.endswith(":free")):
            raise SystemExit(
                f"free_only: openrouter model {model!r} is not a free model "
                "(use openrouter/free or a *:free model)")


def _esc(s: str) -> str:
    """Escape a string for a GitHub Actions annotation message."""
    return (s.replace("%", "%25").replace("\r", "%0D")
             .replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C"))


def failure_annotations(record: dict) -> list[str]:
    """One ::error annotation per failed stage, so a failed dispatch is
    diagnosable from the run's annotations (the trial record itself is an
    artifact; annotations are the API-readable surface)."""
    out = []
    for a in record.get("artifacts", []):
        if not a.get("ok"):
            out.append(
                f"::error title=producer failed::{_esc(str(a.get('provider')))}"
                f"/{_esc(str(a.get('model')))}: "
                f"{_esc(str(a.get('error', 'unknown error'))[:280])}")
    for j in record.get("jevs", []):
        if not j.get("ok"):
            out.append(
                f"::error title=judge failed::{_esc(str(j.get('rationale', 'unknown error'))[:280])}")
    if not (record.get("winner") or {}):
        out.append("::error title=no winner::trial produced no winning "
                   "artifact (see producer/judge annotations above)")
    return out


async def _run(args) -> dict:
    providers = [parse_endpoint(s) for s in args.provider]
    judge = parse_endpoint(args.judge)
    assert_free_only(providers, judge, args.allow_paid)
    rubric = json.loads(args.rubric) if args.rubric else DEFAULT_RUBRIC
    reference = {"text": args.reference} if args.reference else None
    return await run_trial(args.prompt, providers, rubric, judge,
                           reference=reference, task=args.task)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="deepcli.observatory.dispatch")
    p.add_argument("--prompt", required=True)
    p.add_argument("--provider", action="append", required=True,
                   help="producer endpoint prov:model (repeatable)")
    p.add_argument("--judge", required=True,
                   help="judge endpoint prov:model; must differ from producers")
    p.add_argument("--rubric", default="",
                   help="rubric JSON object (default: quality + grounding)")
    p.add_argument("--reference", default="",
                   help="optional reference text for Kev token-F1 verification")
    p.add_argument("--task", default="classifier-smoke")
    p.add_argument("--out", default="trial-record.json")
    p.add_argument("--allow-paid", action="store_true",
                   help="allow non-free routes (owner-gated; default free-only)")
    args = p.parse_args(argv)

    record = asyncio.run(_run(args))
    Path(args.out).write_text(json.dumps(record, indent=2, default=str))
    ok_artifacts = [a for a in record["artifacts"] if a.get("ok")]
    winner = record.get("winner") or {}
    print(f"task={record['task']} "
          f"artifacts_ok={len(ok_artifacts)}/{len(record['artifacts'])} "
          f"winner={winner.get('provider')}/{winner.get('model')} "
          f"composite={winner.get('composite')}")
    if not ok_artifacts or not winner:
        for line in failure_annotations(record):
            print(line)
        print("FAIL: trial produced no winning artifact", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
