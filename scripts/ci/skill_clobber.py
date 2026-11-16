#!/usr/bin/env python3
"""Detect and repair clobbered SKILL.md files (SHE known repair, L1).

A "clobber" is a write that replaced a skill body with a stub instead of
appending to it. Observed stubs on master 2026-10-14..18: ``PLACEHOLDER``,
``PLACEHOLDER_TOO_LARGE``, ``PLACEHOLDER - full content too large for this call``,
``append note here``, and an unexpanded ``$(cat /tmp/...)``. Sizes ranged from
25 KB to 68 KB while a 68 KB normal git commit succeeded, so size alone is not
the trigger; see docs/ops/incidents/2026-10-18-skill-clobber.md.

Content change is judged order-insensitively: the parent's non-blank lines are
compared as a multiset, so moving text costs nothing and only lines that
disappeared count as loss.

CLI:
  skill_clobber.py check  [--base REF] [PATH ...]   # exit 1 if any clobber
  skill_clobber.py repair [--write] PATH ...         # rebuild from last good body
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass

ROOT = pathlib.Path(__file__).resolve().parents[2]

PLACEHOLDER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?im)^\s*PLACEHOLDER(?:[_\s\-:]|$)"),
    re.compile(r"(?i)too large for this call"),
    re.compile(r"(?i)full content too large"),
    re.compile(r"(?im)^\s*append (?:note|content|text) here\s*$"),
    re.compile(r"\$\((?:cat|<)\s"),
    re.compile(r"(?im)^\s*\.\.\.\s*\(?(?:rest|remaining|existing) (?:of )?(?:file|content)"),
)
# Lines a writer adds to excuse a truncation; never carried into a repair.
EXCUSE_LINE = re.compile(r"(?i)(preserved in prior commits|see session note|local stamp complete)")

MAX_LOST_RATIO = 0.5
WARN_LOST_RATIO = 0.10
MIN_LINES_FOR_LOSS_CHECK = 100
MIN_BODY_BYTES = 200  # a tracked skill body smaller than this is a stub
SHRINK_OVERRIDE_TOKEN = "[allow-skill-shrink]"


def _git(*args: str, cwd: pathlib.Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def placeholder_hits(text: str) -> list[str]:
    return [p.pattern for p in PLACEHOLDER_PATTERNS if p.search(text)]


@dataclass
class Delta:
    parent_lines: int
    lost: int
    added: int
    lost_ratio: float
    reordered: bool


def content_delta(before: str, after: str) -> Delta:
    b, a = Counter(_lines(before)), Counter(_lines(after))
    lost = sum((b - a).values())
    added = sum((a - b).values())
    total = sum(b.values()) or 1
    common_b = [ln for ln in _lines(before) if ln in a]
    common_a = [ln for ln in _lines(after) if ln in b]
    return Delta(total, lost, added, lost / total, common_b != common_a)


@dataclass
class Verdict:
    path: str
    clobbered: bool
    reasons: list[str]
    warnings: list[str]
    delta: dict | None


def evaluate(path: str, text: str, parent: str | None, override: bool = False) -> Verdict:
    reasons: list[str] = []
    warnings: list[str] = []
    hits = placeholder_hits(text)
    if hits:
        reasons.append("placeholder body: " + ", ".join(hits))
    if len(text.encode()) < MIN_BODY_BYTES and parent and len(parent.encode()) >= MIN_BODY_BYTES:
        reasons.append(f"stub body ({len(text.encode())} bytes)")
    d = None
    if parent is not None:
        dd = content_delta(parent, text)
        d = asdict(dd)
        if dd.parent_lines >= MIN_LINES_FOR_LOSS_CHECK and dd.lost_ratio > MAX_LOST_RATIO:
            msg = f"lost {dd.lost}/{dd.parent_lines} parent lines ({dd.lost_ratio:.2f})"
            (warnings if override else reasons).append(msg + (" [override]" if override else ""))
        elif dd.lost_ratio > WARN_LOST_RATIO:
            warnings.append(f"lost {dd.lost}/{dd.parent_lines} parent lines ({dd.lost_ratio:.2f}); review")
    return Verdict(path, bool(reasons), reasons, warnings, d)


def show(ref: str, path: str, cwd: pathlib.Path = ROOT) -> str | None:
    r = _git("show", f"{ref}:{path}", cwd=cwd)
    return r.stdout if r.returncode == 0 else None


def last_good(path: str, start: str = "HEAD", cwd: pathlib.Path = ROOT, depth: int = 200) -> tuple[str, str] | None:
    """Newest ancestor version of PATH (from START) with no placeholder and no stub size,
    and not a >50% loss vs the largest version seen in the window."""
    shas = _git("log", f"-{depth}", "--format=%H", start, "--", path, cwd=cwd).stdout.split()
    versions = [(s, show(s, path, cwd)) for s in shas]
    versions = [(s, t) for s, t in versions if t is not None]
    if not versions:
        return None
    peak = max(len(_lines(t)) for _, t in versions)
    for sha, text in versions:
        if placeholder_hits(text) or len(text.encode()) < MIN_BODY_BYTES:
            continue
        if peak >= MIN_LINES_FOR_LOSS_CHECK and len(_lines(text)) < peak * (1 - MAX_LOST_RATIO):
            continue
        return sha, text
    return None


def repair_text(good: str, current: str) -> str:
    """Last good body + any genuinely new lines from CURRENT, appended in their order."""
    have = Counter(_lines(good))
    new_block: list[str] = []
    for raw in current.splitlines():
        s = raw.strip()
        if not s:
            if new_block and new_block[-1] != "":
                new_block.append("")
            continue
        if have[s] > 0:
            have[s] -= 1
            continue
        if placeholder_hits(raw) or EXCUSE_LINE.search(raw):
            continue
        new_block.append(raw.rstrip())
    while new_block and new_block[-1] == "":
        new_block.pop()
    out = good.rstrip("\n") + "\n"
    if new_block:
        out += "\n" + "\n".join(new_block) + "\n"
    return out


def reference_text(path: str, base: str, cwd: pathlib.Path = ROOT) -> tuple[str | None, str]:
    """Text to judge a change against: the parent, unless the parent is itself a stub,
    in which case the last good ancestor. Stops a partial "restore" right after a
    clobber from passing because its parent was a one-line placeholder."""
    parent = show(base, path, cwd)
    if parent is None:
        return None, "none"
    if placeholder_hits(parent) or len(parent.encode()) < MIN_BODY_BYTES:
        lg = last_good(path, base, cwd)
        if lg is not None:
            return lg[1], f"last-good {lg[0][:12]} (parent {base} is a stub)"
    return parent, base


def tracked_skills(cwd: pathlib.Path = ROOT) -> list[str]:
    out = _git("ls-files", cwd=cwd).stdout.splitlines()
    return [p for p in out if p.endswith("/SKILL.md") or p == "SKILL.md"]


def _override(cwd: pathlib.Path) -> bool:
    return SHRINK_OVERRIDE_TOKEN in _git("log", "-1", "--format=%B", cwd=cwd).stdout


def cmd_check(args: argparse.Namespace) -> int:
    paths = args.paths or tracked_skills()
    ov = _override(ROOT)
    bad = []
    for p in paths:
        f = ROOT / p
        if not f.is_file():
            continue
        ref, label = reference_text(p, args.base)
        v = evaluate(p, f.read_text(encoding="utf-8"), ref, ov)
        if v.delta:
            print(f"{p}: vs {label}: lost={v.delta['lost']} added={v.delta['added']} "
                  f"lost_ratio={v.delta['lost_ratio']:.2f} reordered={v.delta['reordered']}")
        for w in v.warnings:
            print(f"::warning file={p}::{w}")
        if v.clobbered:
            bad.append(v)
            print(f"::error file={p}::clobbered: {'; '.join(v.reasons)}")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps([asdict(v) for v in bad], indent=2))
    print(f"skill clobber check: {len(paths)} files, {len(bad)} clobbered")
    return 1 if bad else 0


def cmd_repair(args: argparse.Namespace) -> int:
    rc = 0
    for p in args.paths:
        cur = (ROOT / p).read_text(encoding="utf-8") if (ROOT / p).is_file() else ""
        lg = last_good(p, args.start)
        if lg is None:
            print(f"::error file={p}::no good ancestor found"); rc = 1; continue
        sha, good = lg
        fixed = repair_text(good, cur)
        v = evaluate(p, fixed, good)
        if v.clobbered:
            print(f"::error file={p}::repair still fails: {v.reasons}"); rc = 1; continue
        print(f"{p}: restored from {sha[:12]} ({len(_lines(good))} lines) + {len(_lines(fixed)) - len(_lines(good))} new lines")
        if args.write:
            (ROOT / p).write_text(fixed, encoding="utf-8")
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("paths", nargs="*"); c.add_argument("--base", default="HEAD~1"); c.add_argument("--json")
    r = sub.add_parser("repair"); r.add_argument("paths", nargs="+"); r.add_argument("--start", default="HEAD"); r.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    return cmd_check(a) if a.cmd == "check" else cmd_repair(a)


if __name__ == "__main__":
    sys.exit(main())
