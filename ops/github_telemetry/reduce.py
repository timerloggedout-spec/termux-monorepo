"""Pure reduce: jobs payloads → window stats + CSV-shaped rows."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from she.metrics.job_timestamps import aggregate_workflow_window


def _load_jobs_payload(path: Path) -> Any:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "data" in raw:
        return raw["data"]
    return raw


def reduce_main(args: Any) -> int:
    paths: list[Path] = []
    if args.jobs_file:
        paths.extend(args.jobs_file)
    if args.jobs_glob:
        paths.extend(sorted(Path().glob(args.jobs_glob)))
    if not paths:
        print("reduce: no jobs files", file=sys.stderr)
        return 2

    payloads: list[Any] = []
    run_ids: list[int | None] = []
    for p in paths:
        try:
            data = _load_jobs_payload(p)
        except Exception as e:
            print(f"reduce: skip {p}: {e}", file=sys.stderr)
            continue
        payloads.append(data)
        rid = None
        if isinstance(data, dict):
            # try meta from wrapper or first job
            jobs = data.get("jobs") or []
            if jobs and isinstance(jobs[0], dict) and jobs[0].get("run_id") is not None:
                try:
                    rid = int(jobs[0]["run_id"])
                except (TypeError, ValueError):
                    pass
        run_ids.append(rid)

    if not payloads:
        print("reduce: no valid payloads", file=sys.stderr)
        return 2

    win = aggregate_workflow_window(
        payloads, run_ids=run_ids, window_label=args.window_label
    )
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_json = out_dir / f"actions-performance-reconstructed-{stamp}.json"
    body = {
        **win.to_mapping(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": [str(p) for p in paths],
        "source_count": len(payloads),
    }
    out_json.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_json}")
    print(json.dumps(win.to_mapping(), indent=2))
    return 0
