"""Delphi signal bridge: turns real shadow-lane runs into flywheel feedback (no model calls).

  python3 -m scripts.delphi.signals shadow-outcome --workflow NAME --workflow-id ID
Writes event/rfp/outcome to $GITHUB_OUTPUT (empty event = nothing to send). Stdlib only, names only.
"""
from __future__ import annotations

import argparse, json, os, sys

from scripts.delphi import gate

LANES = os.path.join(gate.ROOT, "ops", "delphi", "shadow-lanes.json")


def decide(conclusions: list[str], labels: set[str], need: int = 3) -> str | None:
    """conclusions newest-first, already filtered to success/failure."""
    if "delphi:shadow" not in labels or not conclusions:
        return None
    if conclusions[0] == "failure" and len(conclusions) > 1 and conclusions[1] == "success":
        return "miss"
    if "delphi:promoted" not in labels and len(conclusions) >= need and all(c == "success" for c in conclusions[:need]):
        return "confirmed"
    return None


def lanes_for(workflow: str, lanes: dict) -> list[str]:
    return [rfp for rfp, l in lanes.get("lanes", {}).items() if workflow in l.get("workflows", [])]


def shadow_outcome(gh: "gate.GH", workflow: str, workflow_id: str, need: int) -> dict:
    lanes = gate.load(LANES)
    for rfp in lanes_for(workflow, lanes):
        labels = {l["name"] for l in gh.req("GET", f"/issues/{rfp}").get("labels", [])}
        runs = gh.req("GET", f"/actions/workflows/{workflow_id}/runs?branch=master&per_page=30").get("workflow_runs", [])
        concl = [r["conclusion"] for r in runs if r.get("conclusion") in ("success", "failure")]
        out = decide(concl, labels, need)
        print(f"::notice::delphi shadow-outcome rfp=#{rfp} workflow={workflow} recent={concl[:need]} decision={out or 'none'}")
        if out:
            return {"event": "delphi-feedback" if out == "confirmed" else "hindsight-forecast-miss", "rfp": rfp, "outcome": out}
    return {"event": "", "rfp": "", "outcome": ""}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="delphi-signals")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shadow-outcome"); s.add_argument("--workflow", required=True); s.add_argument("--workflow-id", required=True)
    a = p.parse_args(argv)
    need = gate.load(gate.PANEL)["award"]["promote_after_confirmed_runs"]
    try:
        res = shadow_outcome(gate.GH(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]), a.workflow, a.workflow_id, need)
    except gate.RateLimited as e:
        print(f"::warning::delphi shadow-outcome deferred on rate limit: {e}")
        res = {"event": "", "rfp": "", "outcome": ""}
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
        for k, v in res.items():
            f.write(f"{k}={v}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
