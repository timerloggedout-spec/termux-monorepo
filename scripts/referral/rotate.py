#!/usr/bin/env python3
"""Automated referral-code rotation engine.

Swaps the next reserve code into a programme's live (or cell_b) slot in
config/referral_programs.json, marks the old code exhausted, rebuilds the
public feed, patches the PARTNERS.md section-1b code cell, and appends a
rotation_log entry to the registry. The landing re-renders from the feed,
so a merged rotation PR is the whole swap: registry -> feed -> landing.

Detection is an input, not a guess: no programme in the registry exposes a
redemption-count API or webhook (audited 2026-10-27), so the trigger is a
named sensor report passed in by the caller:
  --source owner-panel | in-app | visitor-report | pool-watch
  --uses-left N  (sensor reading; rotation fires at/below the programme's
                  rotation.threshold_uses_left, or at 0 = exhausted)
With no --uses-left, the call asserts exhaustion (visitor report path).

Exit codes: 0 rotated · 2 pool empty (programme flipped to code_pending,
log appended, feed rebuilt) · 3 above threshold, no-op · 4 bad input.
Stdlib only. Paths default to repo layout; override for tests.
"""
import argparse, importlib.util, json, pathlib, re, sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_builder(feed_out):
    spec = importlib.util.spec_from_file_location("build_feed", HERE / "build_feed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", required=True)
    ap.add_argument("--cell", choices=["live", "cell_b"], default="live")
    ap.add_argument("--source", required=True,
                    choices=["owner-panel", "in-app", "visitor-report", "pool-watch"])
    ap.add_argument("--uses-left", type=int, default=None)
    ap.add_argument("--registry", default=str(ROOT / "config" / "referral_programs.json"))
    ap.add_argument("--feed", default=str(ROOT / "apps" / "help-wanted-dashboard" / "data" / "referral-feed.json"))
    ap.add_argument("--partners", default=str(ROOT / "docs" / "PARTNERS.md"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    reg_path, feed_path, partners_path = map(pathlib.Path, (a.registry, a.feed, a.partners))
    reg = json.loads(reg_path.read_text())
    prog = next((p for p in reg["programs"] if p["id"] == a.program), None)
    if prog is None:
        print(f"unknown programme {a.program}"); return 4
    codes = prog.get("codes", [])
    if not codes:
        print(f"{a.program}: no code pool (link programme) — rotation n/a"); return 4

    rot = prog.get("rotation", {})
    threshold = rot.get("threshold_uses_left", 5)
    slot_status = "live" if a.cell == "live" else "live_cell_b"
    current = next((c for c in codes if c["status"] == slot_status), None)
    if current is None:
        print(f"{a.program}: no {slot_status} code to rotate"); return 4
    if a.uses_left is not None and a.uses_left > threshold:
        print(f"{a.program}: uses-left {a.uses_left} > threshold {threshold} — no rotation")
        return 3

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"ts": now, "program": a.program, "cell": a.cell, "old_code": current["code"],
             "new_code": None, "source": a.source, "uses_left": a.uses_left,
             "result": None}
    spare = next((c for c in codes if c["status"] == "reserve"), None)
    current["status"] = "exhausted"
    if spare is not None:
        spare["status"] = slot_status
        entry["new_code"] = spare["code"]
        entry["result"] = "rotated"
        rc = 0
    else:
        # Only a dead live cell takes the programme off the public stack;
        # a dead cell_b just ends that A/B cell (live cell keeps serving).
        if a.cell == "live":
            prog["status"] = "code_pending"
        entry["result"] = "pool_empty"
        rc = 2
    reg.setdefault("rotation_log", []).append(entry)

    if not a.dry_run:
        reg_path.write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")
        builder = load_builder(feed_path)
        feed_path.write_text(json.dumps(builder.build(reg), indent=1, sort_keys=True) + "\n")
        if rc == 0 and partners_path.exists():
            text = partners_path.read_text()
            new_text = re.sub(rf"(`){re.escape(current['code'])}(`)",
                              rf"\g<1>{spare['code']}\g<2>", text, count=1)
            if new_text != text:
                partners_path.write_text(new_text)
    print(json.dumps(entry))
    return rc


if __name__ == "__main__":
    sys.exit(main())
