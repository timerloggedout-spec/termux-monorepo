#!/usr/bin/env python3
"""Fleet latency probe — measures inter-network latency as a fleet quantity.

Owner order (2026-11-01): inter-network latency becomes a MEASURED fleet
quantity. This instrument takes unauthenticated HTTPS timing samples of the
surfaces the fleet depends on, using curl's timing variables. Timing is the
product: no authenticated calls are made and no inference/API quota is spent
(401/404 responses are expected on several API surfaces and are fine).

Method per target: N runs (default 3) of
  curl -w '%{time_namelookup} %{time_connect} %{time_appconnect}
           %{time_starttransfer} %{time_total} %{http_code}'
Redirects are NOT followed: a surface's first response (including a 301/302)
is its real edge behaviour and is what gets timed.

Recorded segments (ms): dns and tcp and tls are segment durations derived
from curl's absolute timestamps; ttfb and total are absolute from request
start (curl convention). Medians are taken across successful runs.

Re-measurement is event/state-gated (cadence law): there is no scheduler for
this instrument. The GitHub Actions workflow (.github/workflows/
latency-probe.yml) is workflow_dispatch-only and commits a new report ONLY
when the state gate trips (see gate_deltas). VM-vantage re-runs are
agent-initiated on anomaly events, using this same script.

Stdlib only.
"""

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "fleet-latency/v1"
CURL_FORMAT = (
    "%{time_namelookup} %{time_connect} %{time_appconnect} "
    "%{time_starttransfer} %{time_total} %{http_code}"
)
# State-gate thresholds (owner cadence law, 2026-11-01): a surface counts as
# materially changed only when its median total both moves by more than half
# AND by more than 300 ms in absolute terms — small fast surfaces may swing
# wildly in percentage without mattering, and slow surfaces need a real
# absolute move before a new record is worth committing.
GATE_REL = 0.50
GATE_ABS_MS = 300.0
GATE_EXIT_MATERIAL = 3


def parse_curl_output(text):
    """Parse one curl -w timing line into a run record (ms).

    Raises ValueError on malformed output (including curl's 000 status,
    which means no HTTP response was received).
    """
    parts = text.strip().split()
    if len(parts) != 6:
        raise ValueError(f"expected 6 fields, got {len(parts)}: {text!r}")
    namelookup, connect, appconnect, starttransfer, total = (
        float(p) for p in parts[:5]
    )
    http_status = int(parts[5])
    if http_status == 0:
        raise ValueError("curl reported http_code 000 (no response)")
    dns = namelookup
    tcp = connect - namelookup
    tls = (appconnect - connect) if appconnect > 0 else 0.0
    return {
        "dns_ms": round(dns * 1000, 2),
        "tcp_ms": round(max(tcp, 0.0) * 1000, 2),
        "tls_ms": round(max(tls, 0.0) * 1000, 2),
        "ttfb_ms": round(starttransfer * 1000, 2),
        "total_ms": round(total * 1000, 2),
        "http_status": http_status,
    }


def run_curl(url, timeout=25):
    """One timing sample. Returns a run record, or {'error': ...}."""
    try:
        proc = subprocess.run(
            [
                "curl", "-sS", "-o", "/dev/null",
                "--max-time", str(timeout),
                "-A", "fleet-latency-probe/1.0",
                "-w", CURL_FORMAT,
                url,
            ],
            capture_output=True, text=True, timeout=timeout + 10,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"curl exceeded {timeout + 10}s harness timeout"}
    if proc.returncode != 0:
        return {"error": f"curl exit {proc.returncode}: {proc.stderr.strip()[:200]}"}
    try:
        return parse_curl_output(proc.stdout)
    except ValueError as exc:
        return {"error": f"unparseable curl output: {exc}"}


def median_record(runs):
    """Median timing fields across the successful runs of one target."""
    ok = [r for r in runs if "error" not in r]
    if not ok:
        return None
    med = {}
    for field in ("dns_ms", "tcp_ms", "tls_ms", "ttfb_ms", "total_ms"):
        med[field] = round(statistics.median(r[field] for r in ok), 2)
    # http_status of the median-total run: the most representative response.
    med_total = med["total_ms"]
    rep = min(ok, key=lambda r: abs(r["total_ms"] - med_total))
    med["http_status"] = rep["http_status"]
    return med


def probe_target(target, runs=3, runner=run_curl):
    samples = [runner(target["url"]) for _ in range(runs)]
    med = median_record(samples)
    record = {
        "name": target["name"],
        "url": target["url"],
        "source": target.get("source", ""),
        "runs": samples,
    }
    if med is None:
        record["ok"] = False
        record["error"] = samples[0].get("error", "all runs failed") if samples else "no runs"
        record["median"] = None
        record["http_status"] = None
    else:
        record["ok"] = True
        record["median"] = med
        record["http_status"] = med["http_status"]
    return record


def gate_deltas(current_records, baseline_records,
                rel=GATE_REL, abs_ms=GATE_ABS_MS):
    """State gate: which surfaces materially changed vs the baseline?

    Returns a list of delta dicts. A delta is recorded when:
      * the surface errors / is unreachable now (kind 'error'), or
      * its error state differs from baseline (kind 'state-change'), or
      * median total moved by > rel (fraction) AND > abs_ms (kind 'delta').
    An empty list means: no material delta — commit nothing.
    """
    base = {r["name"]: r for r in baseline_records}
    deltas = []
    for rec in current_records:
        name = rec["name"]
        b = base.get(name)
        if not rec.get("ok"):
            deltas.append({
                "target": name, "kind": "error",
                "detail": rec.get("error", "unreachable"),
                "baseline_total_ms": (b or {}).get("median", {}).get("total_ms")
                if b and b.get("median") else None,
                "current_total_ms": None,
            })
            continue
        if b is not None and not b.get("ok"):
            deltas.append({
                "target": name, "kind": "state-change",
                "detail": "baseline errored, current run succeeded",
                "baseline_total_ms": None,
                "current_total_ms": rec["median"]["total_ms"],
            })
            continue
        if b is None or not b.get("median"):
            continue
        cur_total = rec["median"]["total_ms"]
        base_total = b["median"]["total_ms"]
        if base_total and base_total > 0:
            move = cur_total - base_total
            if abs(move) / base_total > rel and abs(move) > abs_ms:
                deltas.append({
                    "target": name, "kind": "delta",
                    "detail": f"median total {base_total} -> {cur_total} ms "
                              f"({move:+.1f} ms, {move / base_total:+.0%})",
                    "baseline_total_ms": base_total,
                    "current_total_ms": cur_total,
                })
    return deltas


def load_report(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_gate(args):
    baseline = load_report(args.gate[0])
    current = load_report(args.gate[1])
    deltas = gate_deltas(current["records"], baseline["records"])
    print(f"## Latency state gate — baseline {baseline.get('generated_at')} "
          f"({baseline.get('vantage')}) vs current {current.get('generated_at')} "
          f"({current.get('vantage')})")
    if not deltas:
        print("No material delta: every surface within "
              f">{GATE_REL:.0%} AND >{GATE_ABS_MS:.0f} ms of baseline, "
              "and no surface in an error state. Nothing to commit.")
        return 0
    for d in deltas:
        print(f"- MATERIAL [{d['kind']}] {d['target']}: {d['detail']}")
    print(f"{len(deltas)} material delta(s): a new report record is warranted.")
    return GATE_EXIT_MATERIAL


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vantage", choices=("vm", "actions"), default="vm",
                    help="vantage label recorded in the report")
    ap.add_argument("--targets", default=str(Path(__file__).with_name("targets.json")),
                    help="targets JSON (default: targets.json beside this script)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--core-only", action="store_true",
                    help="probe only targets flagged core in targets.json")
    ap.add_argument("--note", default="", help="free-text note stored in the report")
    ap.add_argument("--out", default="", help="write report JSON here (default: stdout)")
    ap.add_argument("--gate", nargs=2, metavar=("BASELINE_JSON", "CURRENT_JSON"),
                    help="compare two report files; exit 0 = no material delta, "
                         f"{GATE_EXIT_MATERIAL} = material delta")
    args = ap.parse_args(argv)

    if args.gate:
        return cmd_gate(args)

    with open(args.targets, "r", encoding="utf-8") as fh:
        targets = json.load(fh)["targets"]
    if args.core_only:
        targets = [t for t in targets if t.get("core")]

    records = [probe_target(t, runs=args.runs) for t in targets]
    report = {
        "schema": SCHEMA,
        "vantage": args.vantage,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool": "ops/latency/probe.py",
        "runs_per_target": args.runs,
        "note": args.note,
        "records": records,
    }
    text = json.dumps(report, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out}: {len(records)} targets, "
              f"{sum(1 for r in records if r['ok'])} ok", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
