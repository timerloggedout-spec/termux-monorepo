#!/usr/bin/env python3
"""Phantom-secret audit + remediation (repo-native, repeatable).

A workflow may reference only secret names verified provisioned
(docs/ops/PHANTOM-SECRETS-AUDIT.md). This script is the repeatable form
of that audit: it compares every `secrets.*` reference in
.github/workflows against the repo's live provisioned inventory (names
only — the API never returns values) and classifies each phantom
reference:

  case-variant   the phantom differs from a provisioned name only by
                 case (e.g. Fly_io_ORG_TOKEN). Fix: repoint.
  dead-branch    the phantom is one branch of a || fallback chain that
                 also names a provisioned secret; the branch can never
                 resolve. Fix: retire the branch (behavior-preserving).
  compiled       the reference lives in a compiled gh-aw .lock.yml;
                 never hand-edited. Disposition: provisioning item.
  provisioning   everything else: an explicit owner provisioning item.
                 No name is ever invented as a replacement.

Subcommands:
  scan    --repo R --workflows DIR --out report.json [--provisioned-file F]
          (without --provisioned-file the inventory is read from the API
          with GH_TOKEN/GITHUB_TOKEN; the scan FAILS if the inventory
          cannot be read or is empty — an empty inventory would make
          every reference look phantom.)
  apply   --class case-variant|dead-branch --workflows DIR --report R
          applies that class's fixes to the working tree.
  render  --report R [--pr-numbers F] --out remediation.md
          renders the remediation document (per-name dispositions plus
          the provisioning checklist).

Stdlib only.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BUILTIN = {"GITHUB_TOKEN"}
CATALOG_FILE = "provision-secrets.yml"
# A secrets.* match is a reference only when not glued to a preceding
# word character (excludes filename fragments like redact_secrets.cjs).
REF_RE = re.compile(r"(?<![A-Za-z0-9_-])secrets\.([A-Za-z_][A-Za-z0-9_]*)")
EXPR_RE = re.compile(r"\$\{\{[^{}]+\}\}")
NAME_RE = re.compile(r"secrets\.([A-Za-z_][A-Za-z0-9_]*)")


def token_re(name):
    return re.compile(r"secrets\." + re.escape(name) + r"(?![A-Za-z0-9_])")


def scan_workflows(workflows_dir):
    """-> {name: {file: [{line, text}]}} for every secrets.* reference."""
    refs = {}
    files = sorted(Path(workflows_dir).glob("*.yml")) + sorted(Path(workflows_dir).glob("*.yaml"))
    for f in files:
        for i, line in enumerate(f.read_text(errors="replace").split("\n"), 1):
            for m in REF_RE.finditer(line):
                refs.setdefault(m.group(1), {}).setdefault(f.name, []).append(
                    {"line": i, "text": line.strip()})
    return refs


def classify(refs, provisioned):
    """Per-reference classification records (pure)."""
    by_lower = {}
    for p in provisioned:
        by_lower.setdefault(p.lower(), p)
    records = []
    for name, files in sorted(refs.items()):
        if name in provisioned or name in BUILTIN:
            continue
        for fn, ctxs in sorted(files.items()):
            for c in ctxs:
                rec = {"name": name, "file": fn, "line": c["line"], "text": c["text"]}
                if fn.endswith(".lock.yml"):
                    rec["class"] = "compiled"
                elif name.lower() in by_lower and by_lower[name.lower()] != name:
                    rec["class"] = "case-variant"
                    rec["replacement"] = by_lower[name.lower()]
                else:
                    m = EXPR_RE.search(c["text"])
                    names = NAME_RE.findall(m.group(0)) if m else []
                    # Dead-branch only when the phantom is a BARE branch of
                    # the chain (removable by the branch grammar). A phantom
                    # behind a condition (matrix.provider == 'x' &&
                    # secrets.Y) is a live conditional reference, not a
                    # dead branch — it is a provisioning item.
                    if (any(n in provisioned for n in names)
                            and m and drop_branch(m.group(0), name) != m.group(0)):
                        rec["class"] = "dead-branch"
                        rec["chain"] = names
                    else:
                        rec["class"] = "provisioning"
                if fn == CATALOG_FILE and rec["class"] == "provisioning":
                    rec["note"] = "provisioning catalog entry (by design)"
                records.append(rec)
    return records


def summarize(records):
    names = sorted({r["name"] for r in records})
    by_class = {}
    for r in records:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    return {"phantom_names": len(names), "references": len(records), "by_class": by_class}


def drop_branch(expr, phantom):
    """Remove one bare `secrets.<phantom>` branch from a || chain,
    preserving all surrounding characters (parens, && suffixes)."""
    pat_head = re.compile(r"secrets\." + re.escape(phantom) + r"(?![A-Za-z0-9_])\s*\|\|\s*")
    pat_mid = re.compile(r"\s*\|\|\s*secrets\." + re.escape(phantom) + r"(?![A-Za-z0-9_])")
    names = NAME_RE.findall(expr)
    if names and names[0] == phantom and pat_head.search(expr):
        return pat_head.sub("", expr, count=1)
    if pat_mid.search(expr):
        return pat_mid.sub("", expr, count=1)
    return expr


def apply_class(workflows_dir, report, cls):
    """Apply one fix class to the working tree. Returns change records."""
    changes = []
    wf = Path(workflows_dir)
    if cls == "case-variant":
        by_file = {}
        for r in report["records"]:
            if r["class"] == "case-variant":
                by_file.setdefault(r["file"], []).append(r)
        for fn, recs in by_file.items():
            p = wf / fn
            text = p.read_text()
            for name in sorted({r["name"] for r in recs}):
                repl = next(r["replacement"] for r in recs if r["name"] == name)
                text, n = token_re(name).subn(f"secrets.{repl}", text)
                if n:
                    changes.append({"file": fn, "name": name, "replacement": repl, "count": n})
            p.write_text(text)
    elif cls == "dead-branch":
        by_file = {}
        for r in report["records"]:
            if r["class"] == "dead-branch":
                by_file.setdefault(r["file"], []).append(r)
        for fn, recs in by_file.items():
            p = wf / fn
            lines = p.read_text().split("\n")
            for i, line in enumerate(lines):
                def fix(m):
                    expr = m.group(0)
                    names = NAME_RE.findall(expr)
                    provisioned_here = [n for n in names
                                        if n in set(report["provisioned"])]
                    if not provisioned_here:
                        return expr
                    new_expr = expr
                    dropped = []
                    for phantom in sorted({n for n in names
                                           if any(r["name"] == n for r in recs)}):
                        after = drop_branch(new_expr, phantom)
                        if after != new_expr:
                            dropped.append(phantom)
                            new_expr = after
                    if not dropped:
                        return expr
                    assert new_expr.count("(") == new_expr.count(")"), new_expr
                    assert any(n in set(report["provisioned"])
                               for n in NAME_RE.findall(new_expr)), new_expr
                    changes.append({"file": fn, "line": i + 1, "dropped": dropped,
                                      "old": expr, "new": new_expr})
                    return new_expr
                lines[i] = EXPR_RE.sub(fix, line)
            p.write_text("\n".join(lines))
    else:
        raise ValueError(f"unknown class {cls}")
    return changes


def fetch_provisioned(repo, token):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/secrets?per_page=100",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return sorted(s["name"] for s in data.get("secrets", []))


def render(report, pr_numbers):
    s = report["summary"]
    out = []
    out.append("# Phantom-Secret Remediation")
    out.append("")
    out.append(f"Generated {report['generated_at']} by the phantom-secrets audit "
               f"(repo-native, repeatable: `.github/workflows/phantom-secrets-audit.yml`). "
               f"Counts are derived live at generation time. Names only — no secret "
               f"values exist in this document.")
    out.append("")
    out.append(f"- Phantom names: **{s['phantom_names']}** across "
               f"**{s['references']}** references")
    for cls, n in sorted(s["by_class"].items()):
        out.append(f"- {cls}: {n} references")
    out.append("")
    cv = [r for r in report["records"] if r["class"] == "case-variant"]
    if cv:
        pr = pr_numbers.get("case-variant")
        out.append(f"## Repointed — case variants" + (f" (PR #{pr})" if pr else ""))
        out.append("")
        seen = {}
        for r in cv:
            seen.setdefault((r["name"], r["replacement"]), set()).add(r["file"])
        for (name, repl), files in sorted(seen.items()):
            out.append(f"- `secrets.{name}` → `secrets.{repl}` "
                       f"(case-variant of the provisioned name) — {', '.join(sorted(files))}")
        out.append("")
    db = [r for r in report["records"] if r["class"] == "dead-branch"]
    if db:
        pr = pr_numbers.get("dead-branch")
        out.append(f"## Retired — dead fallback branches" + (f" (PR #{pr})" if pr else ""))
        out.append("")
        out.append("Each reference below was one branch of a `||` fallback chain that "
                   "also names a provisioned secret; the branch could never resolve and "
                   "was removed. Behavior is unchanged — the chains resolve exactly as "
                   "they did before, now without the phantom name.")
        out.append("")
        seen = {}
        for r in db:
            seen.setdefault(r["name"], set()).add(r["file"])
        for name, files in sorted(seen.items()):
            out.append(f"- `secrets.{name}` — {', '.join(sorted(files))}")
        out.append("")
    prov = [r for r in report["records"] if r["class"] in ("provisioning", "compiled")]
    if prov:
        out.append("## Owner provisioning checklist")
        out.append("")
        out.append("No verified provisioned replacement exists for these names. Each is "
                   "an explicit owner provisioning item: provision the name (with its "
                   "real value) if the integration should be live, or remove the "
                   "reference. Nothing here was guessed or silently mapped.")
        out.append("")
        seen = {}
        for r in prov:
            key = (r["name"], r["class"], r.get("note", ""))
            seen.setdefault(key, set()).add(r["file"])
        for (name, cls, note), files in sorted(seen.items()):
            suffix = f" — {note}" if note else ""
            if cls == "compiled":
                suffix += " — compiled gh-aw lock file; fix at the workflow source, not by hand-editing"
            out.append(f"- [ ] `secrets.{name}` — {', '.join(sorted(files))}{suffix}")
        out.append("")
    out.append("## Rule")
    out.append("")
    out.append("Workflows may reference only verified-provisioned secret names. A new "
               "secret is an owner provisioning act, named explicitly — never an "
               "assumption baked into a workflow.")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("--repo", default="timerloggedout-spec/termux-monorepo")
    sc.add_argument("--workflows", default=".github/workflows")
    sc.add_argument("--out", default="phantom-report.json")
    sc.add_argument("--provisioned-file")
    ap_ = sub.add_parser("apply")
    ap_.add_argument("--class", dest="cls", required=True)
    ap_.add_argument("--workflows", default=".github/workflows")
    ap_.add_argument("--report", default="phantom-report.json")
    rn = sub.add_parser("render")
    rn.add_argument("--report", default="phantom-report.json")
    rn.add_argument("--pr-numbers")
    rn.add_argument("--out", default="PHANTOM-SECRET-REMEDIATION.md")
    args = ap.parse_args()

    if args.cmd == "scan":
        if args.provisioned_file:
            provisioned = json.loads(Path(args.provisioned_file).read_text())
        else:
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if not token:
                print("GH_TOKEN/GITHUB_TOKEN not set", file=sys.stderr)
                return 2
            provisioned = fetch_provisioned(args.repo, token)
        if not provisioned:
            print("provisioned inventory is empty — refusing to scan "
                  "(every reference would look phantom)", file=sys.stderr)
            return 2
        refs = scan_workflows(args.workflows)
        records = classify(refs, set(provisioned))
        report = {"generated_at": datetime.now(timezone.utc).isoformat(),
                  "provisioned": provisioned, "records": records}
        report["summary"] = summarize(records)
        Path(args.out).write_text(json.dumps(report, indent=1, sort_keys=True))
        print(f"scan: {report['summary']}")
        return 0
    if args.cmd == "apply":
        report = json.loads(Path(args.report).read_text())
        changes = apply_class(args.workflows, report, args.cls)
        print(json.dumps(changes, indent=1))
        return 0
    if args.cmd == "render":
        report = json.loads(Path(args.report).read_text())
        pr_numbers = json.loads(Path(args.pr_numbers).read_text()) if args.pr_numbers else {}
        Path(args.out).write_text(render(report, pr_numbers))
        print(f"wrote {args.out}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
