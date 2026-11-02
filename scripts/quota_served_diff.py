#!/usr/bin/env python3
"""Served-vs-record diff probe for the quota surfaces (Hybrid E, owner
decision 2026-11-01). Asserts that what the quota pages SERVE matches
the record on master, and that the record itself is fresh:

  R1  record readings (dashboard data/quota.json) gen-stamp age <= 24h
  R2  record usage pack (ops/quota/quota-usage.json) gen-stamp age <= 24h
  R3  usage-series carries a generated_at stamp (root fix) and the
      dashboard mirror's stamp equals the record's
  R4  every series' last point >= usage-pack gen - EPS (72h): the
      rendered series are not older than the pack they derive from
  S1  per served surface (GitHub Pages + Vercel mirror): served
      data/quota.json gen-stamp == record gen-stamp AND served reading
      count == registry service count
  S2  per served surface: served data/quota-usage.json gen-stamp ==
      record usage-pack gen-stamp
  S3  per served surface: served data/usage-series.json gen-stamp ==
      record usage-series gen-stamp

Exit 0 iff every assertion passes. Verdict lines go to stdout (the
workflow tees them into the step summary). stdlib only.

Usage: python3 scripts/quota_served_diff.py [--root .] [--no-served]
       [--max-age-hours 24] [--eps-hours 72]
"""
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SURFACES = {
    "pages": "https://timerloggedout-spec.github.io/help-wanted",
    "vercel": "https://help-wanted-oversight.vercel.app",
}
READINGS = "apps/help-wanted-dashboard/data/quota.json"
USAGE = "ops/quota/quota-usage.json"
SERIES = "ops/quota/usage-series.json"
SERIES_MIRROR = "apps/help-wanted-dashboard/data/usage-series.json"
USAGE_MIRROR = "apps/help-wanted-dashboard/data/quota-usage.json"
REGISTRY = "ops/quota/registry.json"

RESULTS = []


def report(name, ok, detail):
    RESULTS.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {name} - {detail}")


def parse_ts(v):
    if not isinstance(v, str):
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None


def load(root, rel):
    p = Path(root) / rel
    return json.loads(p.read_text()) if p.exists() else None


def fetch(url):
    req = urllib.request.Request(url + "?probe=served-diff",
                                 headers={"User-Agent": "quota-served-diff"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--no-served", action="store_true")
    ap.add_argument("--max-age-hours", type=float, default=24)
    ap.add_argument("--eps-hours", type=float, default=72)
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    max_age = timedelta(hours=a.max_age_hours)
    eps = timedelta(hours=a.eps_hours)

    registry = load(a.root, REGISTRY) or {}
    reg_count = len(registry.get("services", []))
    readings = load(a.root, READINGS) or {}
    usage = load(a.root, USAGE) or {}
    series = load(a.root, SERIES) or {}
    series_mirror = load(a.root, SERIES_MIRROR) or {}
    usage_mirror = load(a.root, USAGE_MIRROR) or {}

    r_gen = parse_ts(readings.get("generated_at"))
    report("R1 readings-fresh", bool(r_gen and now - r_gen <= max_age),
           f"record gen={readings.get('generated_at')} age<=24h")
    u_gen = parse_ts(usage.get("generated_at"))
    report("R2 usage-fresh", bool(u_gen and now - u_gen <= max_age),
           f"usage-pack gen={usage.get('generated_at')} age<=24h")
    s_gen = series.get("generated_at")
    report("R3 series-stamped", bool(parse_ts(s_gen)),
           f"usage-series generated_at={s_gen}")
    report("R3b series-mirror-eq",
           series_mirror.get("generated_at") == s_gen and s_gen is not None,
           f"mirror gen={series_mirror.get('generated_at')}")
    report("R3c usage-mirror-eq",
           usage_mirror.get("generated_at") == usage.get("generated_at")
           and usage.get("generated_at") is not None,
           f"mirror gen={usage_mirror.get('generated_at')}")

    if u_gen:
        floor = u_gen - eps
        ends = []
        for axis in (series.get("axes") or {}).values():
            for s in axis:
                pts = s.get("points") or []
                if pts:
                    ends.append((s.get("key"), parse_ts(pts[-1].get("t"))))
        bad = [(k, t) for k, t in ends if t is None or t < floor]
        report("R4 series-ends", not bad,
               f"{len(ends)} series, floor={floor.isoformat()}, bad={bad}")
    else:
        report("R4 series-ends", False, "usage-pack gen missing")

    if not a.no_served:
        for name, base in SURFACES.items():
            try:
                sq = fetch(f"{base}/data/quota.json")
                ok = (sq.get("generated_at") == readings.get("generated_at")
                      and len(sq.get("readings", [])) == reg_count)
                report(f"S1 {name} quota-eq",
                       ok,
                       f"served gen={sq.get('generated_at')} "
                       f"readings={len(sq.get('readings', []))} "
                       f"registry={reg_count}")
            except Exception as e:  # unreachable surface = divergence
                report(f"S1 {name} quota-eq", False, f"fetch failed: {e}")
            try:
                su = fetch(f"{base}/data/quota-usage.json")
                report(f"S2 {name} usage-eq",
                       su.get("generated_at") == usage.get("generated_at"),
                       f"served gen={su.get('generated_at')}")
            except Exception as e:
                report(f"S2 {name} usage-eq", False, f"fetch failed: {e}")
            try:
                ss = fetch(f"{base}/data/usage-series.json")
                report(f"S3 {name} series-eq",
                       ss.get("generated_at") == s_gen and s_gen is not None,
                       f"served gen={ss.get('generated_at')}")
            except Exception as e:
                report(f"S3 {name} series-eq", False, f"fetch failed: {e}")

    verdict = all(RESULTS)
    print(f"verdict={'PASS' if verdict else 'FAIL'} "
          f"({sum(RESULTS)}/{len(RESULTS)} assertions)")
    out = Path(__import__("os").environ.get("GITHUB_OUTPUT", "/dev/null"))
    try:
        with out.open("a") as fh:
            fh.write(f"verdict={'PASS' if verdict else 'FAIL'}\n")
    except OSError:
        pass
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
