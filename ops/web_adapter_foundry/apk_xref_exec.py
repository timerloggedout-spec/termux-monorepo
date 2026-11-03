#!/usr/bin/env python3
"""apk-xref execution runner — one filed [apk-xref] request issue in,
one findings filing out. Driven by .github/workflows/apk-xref-exec.yml
in an ephemeral Actions runner (owner ENV rule: swarm execution runs
in GitHub Actions isolation, not on a VM or a device).

Pipeline: parse the request filing (form headings) -> belt acquire
(exit 3 = no artifact, an evidence outcome, not a failure) -> extract
-> clone the target repo -> scan-repo -> xref; or, when no artifact is
acquired, the belt no-artifact record with the sources checked. The
findings markdown is the belt's own render (apk-xref/v1 keys verbatim,
form headings verbatim — the PR #2143 seam). Filing the findings issue
and commenting stays in the workflow shell (gh), so this runner is
deterministic file-in/file-out and unit-testable offline.

Stdlib only.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BELT = Path(__file__).with_name("apk_xref.py")
SUBMITTER = "reverse-engineering-toolkits{apk-xref-exec}"
_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)


def parse_filing(body: str) -> dict:
    """Form body -> {label: value} from `### Label` sections."""
    fields: dict[str, str] = {}
    parts = _HEADING.split(body or "")
    # parts: [pre, label, value, label, value, ...]
    for i in range(1, len(parts) - 1, 2):
        fields[parts[i].strip()] = parts[i + 1].strip()
    return fields


_MISSING = {"", "none", "none-known", "n/a", "unknown"}
_PKG_RE = re.compile(r"\b[a-z][a-z0-9]*(?:\.[a-z0-9_]+){2,}\b")
_NOT_PKG_TLD = {"com", "org", "net", "io", "de", "dev", "app", "html",
                "json", "md", "py", "yml", "yaml", "apk"}


def _scan_package_id(body: str) -> str:
    """Fallback: find a package-id-shaped token in the filing body
    (URLs stripped first, file/TLD endings rejected). Filing #2297's
    2026-11-03 run reached the belt with package_id empty although
    the package existed on the filed route — a silent spec gap that
    must not recur: if the Package ID field is unusable, the body
    itself is the next source of truth."""
    text = re.sub(r"https?://\S+", " ", body or "")
    for m in _PKG_RE.finditer(text):
        tok = m.group(0)
        if tok.rsplit(".", 1)[-1] in _NOT_PKG_TLD:
            continue
        return tok
    return ""


def filing_spec(fields: dict, body: str = "") -> dict:
    """The acquire spec + run identity from a parsed request filing."""
    package_id = fields.get("Package ID", "").strip()
    via = "field"
    if package_id.lower() in _MISSING:
        package_id = _scan_package_id(body)
        via = "body-scan" if package_id else "none"
    return {
        "target_id": fields.get("Target ID", "").strip(),
        "repo": fields.get("Target repo URL", "").strip(),
        "source": fields.get("Artifact source", "none-known").strip()
        or "none-known",
        "package_id": package_id,
        "package_id_via": via,
        "evidence": fields.get("Evidence expectation", "reproduced").strip()
        or "reproduced",
    }


ISSUE_BODY_LIMIT = 60_000  # GitHub issue bodies cap at 65,536 chars;
# stay under it (run 41369356763: agora findings exceeded the cap and
# the findings issue could not be created at all).
_ELISION = ("… [elided {n} entries — the full findings record is in "
            "the run's evidence artifact (findings-full.md)]")


def cap_findings_markdown(text: str, limit: int = ISSUE_BODY_LIMIT) -> str:
    """Shrink a findings filing to the issue-body limit by eliding
    list sections longest-first. Headings (the parser's seam) are
    never dropped; the unabridged text travels as findings-full.md
    in the evidence artifact. Returns the (possibly unchanged) text.
    """
    if len(text) <= limit:
        return text
    sections = re.split(r"(?m)(?=^### )", text)
    for keep in (100, 40, 15, 5, 2):
        out = []
        for sec in sections:
            lines = sec.splitlines()
            body = [ln for ln in lines[1:] if ln.strip()]
            if len(body) > keep + 1:
                head = [lines[0]] if lines and lines[0].startswith("###") else []
                elided = len(body) - keep
                sec = "\n".join(head + body[:keep] +
                                 ["", _ELISION.format(n=elided), ""])
            out.append(sec)
        text = "".join(out) if out[0].startswith("###") else "\n".join(out)
        if len(text) <= limit:
            return text
    return text[:limit]

def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def _belt(args: list[str], expect: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    r = _run([sys.executable, str(BELT), *args])
    if r.returncode not in expect:
        raise RuntimeError(f"belt {' '.join(args[:1])} exited {r.returncode}: "
                           f"{r.stderr.strip()[:400]}")
    return r


def execute(fields: dict, issue_number: int, workdir: Path,
            body: str = "") -> dict:
    """Run the belt pipeline. Returns the run summary dict; writes
    findings.md + findings.json into workdir."""
    spec = filing_spec(fields, body)
    if not spec["target_id"]:
        raise ValueError("filing has no Target ID")
    workdir.mkdir(parents=True, exist_ok=True)
    art_dir = workdir / "artifact"
    acq = _belt(["acquire", "--source", spec["source"],
                 "--repo", spec["repo"], "--package-id", spec["package_id"],
                 "--out", str(art_dir)], expect=(0, 3))
    acquisition = json.loads(acq.stdout)
    summary = {"target_id": spec["target_id"], "issue": issue_number,
               "source": spec["source"],
               "spec_package_id": spec["package_id"],
               "spec_package_id_via": spec["package_id_via"],
               "spec_repo": spec["repo"],
               "acquisition_status": acquisition.get("status")}
    common = ["--target-id", spec["target_id"],
              "--xref-issue", f"#{issue_number}",
              "--submitter", SUBMITTER,
              "--artifact-source", spec["source"]]
    if acquisition.get("status") != "acquired":
        checked = acquisition.get("sources_checked") or [spec["source"]]
        _belt(["no-artifact", *common, "--evidence", "observed",
               "--sources-checked", *checked,
               "--out", str(workdir / "findings.json"),
               "--markdown", str(workdir / "findings.md")])
        summary["verdict"] = "no-artifact-found"
        _finalize_findings(workdir, summary)
        return summary

    apk_path = acquisition["path"]
    ext_path = workdir / "extraction.json"
    _belt(["extract", apk_path, "--out", str(ext_path)])
    extraction = json.loads(ext_path.read_text(encoding="utf-8"))
    extraction["provenance"] = acquisition  # xref reads provenance here
    ext_path.write_text(json.dumps(extraction, indent=1), encoding="utf-8")

    src_dir = workdir / "src"
    clone = _run(["git", "clone", "--depth", "1", "--quiet",
                  spec["repo"], str(src_dir)])
    summary["clone_ok"] = clone.returncode == 0
    if clone.returncode != 0:
        src_dir.mkdir(parents=True, exist_ok=True)  # empty tree -> claims ∅
        summary["clone_error"] = clone.stderr.strip()[:300]
    claims_path = workdir / "claims.json"
    _belt(["scan-repo", str(src_dir), "--out", str(claims_path)])

    record_path = workdir / "findings.json"
    _belt(["xref", "--extraction", str(ext_path),
           "--claims", str(claims_path), *common,
           "--evidence", spec["evidence"],
           "--out", str(record_path),
           "--markdown", str(workdir / "findings.md")])
    record = json.loads(record_path.read_text(encoding="utf-8"))
    summary["verdict"] = record.get("verdict")
    summary["package_id"] = record.get("package_id")
    _finalize_findings(workdir, summary)
    return summary


def _finalize_findings(workdir: Path, summary: dict) -> None:
    """Write findings-full.md (unabridged) and cap findings.md (the
    filed body) to the issue-body limit."""
    md = workdir / "findings.md"
    text = md.read_text(encoding="utf-8")
    (workdir / "findings-full.md").write_text(text, encoding="utf-8")
    capped = cap_findings_markdown(text)
    summary["findings_chars_full"] = len(text)
    summary["findings_capped"] = capped != text
    if capped != text:
        md.write_text(capped, encoding="utf-8")

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="apk_xref_exec")
    ap.add_argument("--issue-body", required=True)
    ap.add_argument("--issue-number", required=True, type=int)
    ap.add_argument("--workdir", required=True)
    args = ap.parse_args(argv)
    body = Path(args.issue_body).read_text(encoding="utf-8")
    summary = execute(parse_filing(body), args.issue_number,
                      Path(args.workdir), body)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
