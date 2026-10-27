#!/usr/bin/env python3
"""Quota TUI renderer for termux-monorepo.

Zero-dependency (Python 3 stdlib only) terminal renderer for the quota
panel data. Shared source of truth is the same pair the web panel uses:

  * Registry  -- schema ``3l0.quota-registry.v1``
                 (master: ``ops/quota/registry.json``;
                  local:  ``quota_registry.json``)
                 ALL documented services + entitlements.
  * Readings  -- schema ``3l0.quota-readings.v1``
                 (master: ``apps/help-wanted-dashboard/data/quota.json``
                  == ``docs/ops/generated/quota-status.json``;
                  local:  ``quota-panel/quota.json``)
                 Live/reported readings only (sparse -- most services
                 have no live reading).

Rules honoured (from the registry itself):
  * Documented limits are ENTITLEMENTS, not balances.
  * NEVER invent a remaining/used value. A used/balance line is shown
    only when a reading carries a non-null ``used``. Otherwise the
    renderer prints ``No live reading``.

Usage:
  quota_tui.py [--once] [--no-color] [--width N]
               [--registry PATH] [QUOTA_JSON]

  QUOTA_JSON may be a readings file, a registry file, or a merged
  file containing both ``services`` and ``readings`` keys.
  If no registry is given/found, readings-only input renders just the
  readings; registry-only input renders all services with
  ``No live reading`` status.

Modes:
  --once   print one frame and exit (scripting / testing / pipes)
  (default, on a TTY)  refresh loop; q / Ctrl-C to quit
  (default, not a TTY) same as --once
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[1;31m"
RED_BG = "\033[1;37;41m"
YELLOW = "\033[1;33m"
GREEN = "\033[32m"
CYAN = "\033[1;36m"

USE_COLOR = True


def c(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if USE_COLOR else text


# Statuses that must stand out, worst first. Mirrors the web panel's
# Needs attention set (quota.html): a stale or merely reported problem
# state still surfaces — labelled as what it is, never upgraded to a
# live state — instead of the text lane claiming "no problem state"
# while the panel shows the same reading as an alert.
ALERT_ORDER = {"cap_tripped": 0, "exhausted": 0, "watch": 1, "reported": 2, "stale": 3}
ALERT_LABEL = {
    "cap_tripped": "!! CAP TRIPPED",
    "exhausted": "!! EXHAUSTED",
    "watch": "!  WATCH",
    "ok": "OK",
}


def status_style(status: str | None) -> tuple[str, str]:
    """Return (label, ansi-code) for a reading status."""
    if status is None:
        return ("No live reading", DIM)
    label = ALERT_LABEL.get(status, status.upper())
    if status in ("cap_tripped", "exhausted"):
        return (label, RED_BG)
    if status == "watch":
        return (label, YELLOW)
    if status == "ok":
        return (label, GREEN)
    return (label, CYAN)


# ------------------------------------------------------------- loading
def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def split_data(data: dict) -> tuple[list[dict], list[dict], dict]:
    """Split any accepted input shape into (services, readings, meta)."""
    services = data.get("services") or []
    readings = data.get("readings") or []
    # A bare readings file: schema 3l0.quota-readings.v1
    # A bare registry file:  schema 3l0.quota-registry.v1 (services only)
    return services, readings, data


def candidate_paths(script_dir: Path) -> tuple[list[Path], list[Path]]:
    """Default search paths, relative to cwd and to this script.

    The workspace layout mirrors the repo layout for these artifacts:
        <root>/quota_registry.json          (registry)
        <root>/quota-panel/quota.json       (readings, local build copy)
        <root>/apps/help-wanted-dashboard/data/quota.json  (repo path)
        <root>/docs/ops/generated/quota-status.json        (repo path)
    """
    roots = [Path.cwd(), script_dir, script_dir.parent]
    readings = []
    registry = []
    for r in roots:
        readings += [
            r / "quota.json",
            r / "quota-panel" / "quota.json",
            r / "apps/help-wanted-dashboard/data/quota.json",
            r / "docs/ops/generated/quota-status.json",
        ]
        registry += [
            r / "quota_registry.json",
            r / "registry.json",
            r / "ops/quota/registry.json",
            r / "quota-panel/quota_registry.json",
        ]
    # de-dup, keep order
    def dedup(seq):
        seen, out = set(), []
        for p in seq:
            k = str(p)
            if k not in seen:
                seen.add(k)
                out.append(p)
        return out
    return dedup(readings), dedup(registry)


def first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


# ------------------------------------------------------------ rendering
def fmt_limit(limit, unit: str | None) -> str:
    if limit is None:
        return "n/a" + (f" {unit}" if unit else "")
    return f"{limit} {unit}".strip()


def wrap(text: str, width: int, indent: str = "  ") -> list[str]:
    if not text:
        return []
    return textwrap.wrap(
        text, width=width, initial_indent=indent,
        subsequent_indent=indent, break_long_words=False,
        break_on_hyphens=False,
    ) or [indent + text]


def public_readings(services: list[dict], readings: list[dict], now=None) -> list[dict]:
    """Allowlist display metadata; never expose private account balances or notes."""
    now = datetime.now(timezone.utc) if now is None else now
    by_id, seen = {}, set()
    lanes = {s.get("id"): s.get("lane") for s in services}
    for raw in readings:
        sid = raw.get("resource_id")
        if not isinstance(sid, str):
            continue
        sid = sid.removeprefix("quota:")
        row = {"resource_id": sid, "status": "unknown"}
        if sid in seen:
            by_id[sid] = row
            continue
        seen.add(sid)
        if lanes.get(sid) == "model":
            row["status"] = "private_preflight"
        else:
            try:
                stamp = datetime.fromisoformat(raw["observed_at"].replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    raise ValueError("timezone required")
                age = (now - stamp).total_seconds()
                if age < 0:
                    pass
                elif age > 900:
                    row["status"] = "stale"
                elif raw.get("horizon") != "H0" or raw.get("evidence_status") != "confirmed":
                    row["status"] = "reported"
                elif raw.get("status") in {"ok", "watch", "exhausted", "cap_tripped"}:
                    reset = raw.get("reset")
                    if reset is None or datetime.fromisoformat(reset.replace("Z", "+00:00")) > now:
                        row["status"] = raw["status"]
            except (KeyError, ValueError, TypeError, AttributeError):
                pass
        by_id[sid] = row
    return list(by_id.values())


def render(services: list[dict], readings: list[dict], meta: dict,
           width: int, source_label: str, now=None) -> str:
    width = max(40, min(width, 200))
    readings = public_readings(services, readings, now)
    by_id = {r.get("resource_id"): r for r in readings if r.get("resource_id")}

    # If we only got readings (no registry), synthesise service rows
    # from the readings themselves so nothing is dropped.
    if not services and readings:
        services = [{
            "id": r["resource_id"],
            "provider": r["resource_id"].split(".")[0],
            "metric": "",
            "limit": r.get("limit"),
            "unit": r.get("unit"),
            "window": "",
            "reset": r.get("reset"),
            "live": "",
        } for r in readings]

    def alert_rank(svc: dict) -> tuple[int, str]:
        r = by_id.get(svc.get("id"))
        return (ALERT_ORDER.get(r["status"], 4) if r else 5, svc.get("id", ""))

    alerts = [s for s in services
              if (r := by_id.get(s.get("id"))) and r.get("status") in ALERT_ORDER]
    alerts.sort(key=alert_rank)

    lines: list[str] = []
    rule = "=" * width
    thin = "-" * width
    lines.append(c(rule, CYAN))
    lines.append(c(" QUOTA  termux-monorepo", BOLD) +
                 f"  ({len(services)} registry records)")
    gen = meta.get("generated_at")
    if gen:
        lines.append(f" Snapshot generated (not observation time): {gen}")
    lines.extend(wrap(f"Source: {source_label}", width, indent=" "))
    lines.append(" Limits are documented entitlements, not balances.")
    lines.append(" Private balances are hidden; unknown is not healthy or admitted.")
    lines.append(c(rule, CYAN))

    # ---- alerts first -------------------------------------------------
    lines.append("")
    lines.append(c(" ALERTS", BOLD))
    lines.append(thin)
    if not alerts:
        lines.append("  No services are reporting a problem state.")
        if not readings:
            lines.append("  (No live readings in the input at all.)")
    for svc in alerts:
        r = by_id[svc["id"]]
        label, style = status_style(r.get("status"))
        lines.append(f" {c('[' + label + ']', style)} {svc['id']}")
        lines.extend(wrap(
            f"limit (documented): "
            f"{fmt_limit(r.get('limit', svc.get('limit')), svc.get('unit') or r.get('unit') or '')}",
            width, indent="   "))
        if r.get("used") is not None:
            lines.append(f"   used (live reading): {r['used']}")
        else:
            lines.append("   used: No live reading")
        if r.get("reset"):
            lines.append(f"   reset: {r['reset']}")
        lines.extend(wrap(r.get("note", ""), width, indent="   "))
    # readings that have no matching registry service: never drop them
    known = {s.get("id") for s in services}
    for r in readings:
        if r.get("resource_id") not in known:
            label, style = status_style(r.get("status"))
            lines.append(f" {c('[' + label + ']', style)} {r.get('resource_id')}")
            lines.extend(wrap(r.get("note", ""), width, indent="   "))

    # ---- all services ---------------------------------------------------
    lines.append("")
    lines.append(c(" ALL SERVICES", BOLD))
    lines.append(thin)
    providers: dict[str, list[dict]] = {}
    for svc in services:
        providers.setdefault(svc.get("provider") or "other", []).append(svc)
    for provider in sorted(providers):
        rows = sorted(providers[provider], key=lambda s: s.get("id", ""))
        lines.append(c(f" {provider} ({len(rows)})", CYAN))
        for svc in rows:
            r = by_id.get(svc.get("id"))
            label, style = status_style(r.get("status") if r else None)
            lines.append(f"  {svc.get('id', '?')}")
            lines.append(f"    status: {c(label, style)}")
            lines.extend(wrap(
                f"limit (documented): "
                f"{fmt_limit(svc.get('limit'), svc.get('unit'))}",
                width, indent="    "))
            detail = []
            if svc.get("metric"):
                detail.append(f"metric: {svc['metric']}")
            if svc.get("window"):
                detail.append(f"window: {svc['window']}")
            if svc.get("reset"):
                detail.append(f"reset: {svc['reset']}")
            lines.extend(wrap(" | ".join(detail), width, indent="    "))
            if r is not None:
                if r.get("used") is not None and r.get("limit") is not None:
                    lines.append(f"    live reading: used {r['used']} / "
                                 f"{r['limit']} {r.get('unit') or ''}".rstrip())
                elif r.get("used") is not None:
                    lines.append(f"    live reading: used {r['used']}")
                else:
                    # Reading exists but carries no used value: say so,
                    # do not synthesise a balance from the limit.
                    lines.extend(wrap(
                        "Public evidence state only; no account balance or runtime "
                        "admission implied.", width, indent="    "))
                if r.get("note"):
                    lines.extend(wrap(f"note: {r['note']}", width,
                                      indent="    "))
            else:
                live = svc.get("live")
                suffix = f" (live source: {live})" if live else ""
                lines.extend(wrap(f"No live reading{suffix}", width,
                                  indent="    "))
        lines.append(thin)

    families = meta.get("provider_quota_coverage", {}).get("provider_families", [])
    if families:
        lines.append(" PROVIDER QUOTA-MANAGER COVERAGE (metadata only)")
        for family in families:
            lines.extend(wrap(
                f"{family['provider_family']}: {family['quota_manager_owner']} / "
                f"{family['freshness_owner']}; {family['observation_method']}; "
                f"registry: {', '.join(family['service_ids']) or 'MISSING — explicit gap'}",
                width, indent="  "))
        lines.append(" Coverage and quota checks do not grant runtime admission.")

    n_alert = len(alerts)
    n_live = len(by_id)
    lines.extend(wrap(
        f"{len(services)} registry records | {n_alert} alert(s) | "
        f"{n_live} with a reported reading | "
        f"{len(services) - n_live} with No live reading",
        width, indent=" "))
    lines.append(c(rule, CYAN))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    global USE_COLOR
    ap = argparse.ArgumentParser(description="Quota TUI renderer")
    ap.add_argument("quota_json", nargs="?", default=None,
                    help="quota.json (readings, registry, or merged)")
    ap.add_argument("--registry", default=None,
                    help="registry JSON (3l0.quota-registry.v1)")
    ap.add_argument("--coverage", default=None,
                    help="public provider-quota-coverage/v1 metadata (default: repository snapshot)")
    ap.add_argument("--once", action="store_true",
                    help="print one frame and exit")
    ap.add_argument("--snapshot", action="store_true",
                    help="render as of the readings snapshot's generated_at "
                         "instead of wall-clock now; makes regenerating "
                         "apps/help-wanted-dashboard/quota.txt deterministic "
                         "(statuses as they stood at snapshot generation)")
    ap.add_argument("--no-color", action="store_true",
                    help="disable ANSI colours")
    ap.add_argument("--width", type=int, default=None,
                    help="render width (default: terminal, capped at 80)")
    ap.add_argument("--interval", type=float, default=30.0,
                    help="refresh seconds in interactive mode")
    args = ap.parse_args(argv)

    # Colour only on a real TTY, unless explicitly disabled.
    # Piped/redirected output (e.g. sample-output.txt) stays clean.
    USE_COLOR = sys.stdout.isatty() and not args.no_color \
        and not os.environ.get("NO_COLOR")
    width = args.width or min(os.get_terminal_size().columns
                              if sys.stdout.isatty() else 80, 80)

    script_dir = Path(__file__).resolve().parent
    read_cands, reg_cands = candidate_paths(script_dir)

    services: list[dict] = []
    readings: list[dict] = []
    meta: dict = {}
    sources: list[str] = []

    main_path = Path(args.quota_json) if args.quota_json \
        else first_existing(read_cands)
    if main_path is None:
        print("quota_tui: no quota.json found. Pass a path, e.g.\n"
              "  quota_tui.py ../quota-panel/quota.json", file=sys.stderr)
        return 2
    data = load_json(main_path)
    services, readings, meta = split_data(data)
    sources.append(str(main_path))

    # Registry: explicit, else auto-discover when main input lacks services.
    if not services:
        reg_path = None
        if args.registry:
            cand = Path(args.registry)
            if cand.is_file():
                reg_path = cand
            else:
                print(f"quota_tui: registry not found, ignoring: "
                      f"{args.registry}", file=sys.stderr)
        else:
            reg_path = first_existing(reg_cands)
        if reg_path and reg_path.resolve() != main_path.resolve():
            reg = load_json(reg_path)
            services = reg.get("services") or []
            if services:
                sources.append(str(reg_path))
    elif args.registry and Path(args.registry).is_file():
        reg = load_json(Path(args.registry))
        if reg.get("services"):
            services = reg["services"]
            sources.append(args.registry)
    # Readings may also live in a second file when main input was registry.
    if not readings:
        rd_path = first_existing(read_cands)
        if rd_path and (not main_path or rd_path.resolve() != main_path.resolve()):
            rd = load_json(rd_path)
            if rd.get("readings"):
                readings = rd["readings"]
                meta = {**rd, **{k: v for k, v in meta.items() if v}}
                sources.append(str(rd_path))

    coverage_path = Path(args.coverage) if args.coverage else script_dir.parent / "apps/help-wanted-dashboard/data/provider-quota-coverage.json"
    coverage = load_json(coverage_path) if coverage_path.is_file() else {}
    if coverage.get("schema") != "provider-quota-coverage/v1":
        coverage = {}
    source_label = " + ".join(sources)

    snap_now = None
    if args.snapshot:
        gen = meta.get("generated_at")
        try:
            snap_now = datetime.fromisoformat(str(gen).replace("Z", "+00:00"))
            if snap_now.tzinfo is None:
                raise ValueError("generated_at needs a timezone")
        except (TypeError, ValueError):
            print(f"quota_tui: --snapshot needs a generated_at in the readings input, got: {gen!r}",
                  file=sys.stderr)
            return 2

    def frame() -> str:
        return render(services, readings, {**meta, "provider_quota_coverage": coverage}, width, source_label,
                      now=snap_now)

    if args.once or not sys.stdout.isatty():
        sys.stdout.write(frame())
        return 0

    # Interactive loop (TTY): redraw on interval; q / Ctrl-C quits.
    try:
        while True:
            sys.stdout.write("\033[2J\033[H" + frame())
            sys.stdout.flush()
            time.sleep(args.interval)
            # Reload so a refreshed poller file shows up live.
            try:
                d2 = load_json(main_path)
                s2, r2, m2 = split_data(d2)
                if s2:
                    services = s2
                if r2:
                    readings = r2
                meta = m2 or meta
            except Exception:
                pass
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
