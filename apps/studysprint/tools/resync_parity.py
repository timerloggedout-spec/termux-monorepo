"""Automated re-sync parity tool for StudySprint (Nov 3 re-sync test).

Verifies blob parity between this monorepo's apps/studysprint tree and the
timerloggedout-spec/studysprint repo tree (or a local checkout directory).
Reports per-file identical/differs/missing and exits non-zero on drift.

Offline-runnable against the GitHub API, local directory comparison,
or an offline baseline manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_REPO = "timerloggedout-spec/studysprint"
DEFAULT_BRANCH = "main"

# Baseline manifest frozen for offline validation when network is unavailable
# and no local checkout is specified.
BASELINE_BLOBS: dict[str, str] = {
    "BUILD-BRIEF.md": "1a8c5511471ef51f8cccadafb9caa288d33843b0",
    "CHANGELOG.md": "7b61fea7e87746cc78da887248874d17336db52d",
    "FEATURES.md": "cfbd867cdc1df5d99d34cd088d193c1d03ff7fc0",
    "README.md": "a1578e2fcdf8723a73790512a28b9ed5ae1ea415",
    "VERSION": "6e8bf73aa550d4c57f6f35830f1bcdc7a4a62f38",
    "VERSIONING.md": "c976b97284d46d48e935a82a3427c2720605e099",
    "agent.py": "016bae8edca40ffaf8a3da8e6daf69a9187eb282",
    "article.md": "94a10ddbc436a6642679c9d9a63ce5eac38f2a55",
    "demo-script.md": "183d1bdc02d26db23080d31ac1b588b195f50cdb",
    "demo.py": "f28c2b3bd9d514e1181be8d061a4a1670fafbe3d",
    "evidence/demo-run.json": "20473aedd0cd2e56e56d1dc3f34bfea0246eefda",
    "examples/practice_set.json": "df8937d78880b86ff69c5299607ab65fb34ed49b",
    "examples/syllabus.json": "753751e12864d05116f79455448c3bda3a27539e",
    "foundation/D0-FOUNDATION.md": "0ea19ad3f63d552115fb481ea8a187ca212740c4",
    "foundation/fetch_evidence.py": "8442d8135ee276c16290e770ce6f37595f575ce0",
    "foundation/oracle_kernel.py": "9a4a1c78bf4367ab8805d3d55357700a776bbbb0",
    "requirements.txt": "1dbcb403bf38cd96e49badb4b95f0fc45a98be25",
    "study_tools.py": "2c9bce77314b593d9a9141c63ed2907abe1fae9c",
    "tests/test_studysprint.py": "3bc990693362bca695c16431f386bcb68c572c48",
}


def compute_git_blob_sha(content: bytes) -> str:
    """Compute the SHA1 git blob hash: sha1("blob " + len + "\\0" + content)."""
    header = f"blob {len(content)}\0".encode("utf-8")
    return hashlib.sha1(header + content).hexdigest()


def scan_local_tree(directory: Path, ignore_patterns: set[str] | None = None) -> dict[str, str]:
    """Scan directory recursively and return map of rel_path -> git blob sha."""
    ignore_patterns = ignore_patterns or {"__pycache__", ".pytest_cache", ".git"}
    blobs: dict[str, str] = {}
    directory = directory.resolve()

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_patterns and not d.startswith(".")]
        for file in sorted(files):
            if file.endswith(".pyc") or file.startswith("."):
                continue
            full_path = Path(root) / file
            rel_path = full_path.relative_to(directory).as_posix()
            try:
                content = full_path.read_bytes()
                blobs[rel_path] = compute_git_blob_sha(content)
            except OSError:
                continue
    return blobs


def fetch_github_tree_blobs(repo: str = DEFAULT_REPO, branch: str = DEFAULT_BRANCH,
                            token: str | None = None) -> dict[str, str]:
    """Fetch tree blobs from GitHub REST API."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    headers = {"User-Agent": "studysprint-parity-audit", "Accept": "application/vnd.github.v3+json"}
    token = token or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tree = data.get("tree") or []
            return {
                item["path"]: item["sha"]
                for item in tree
                if item.get("type") == "blob"
            }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch tree from GitHub {repo}@{branch}: {e}") from e


def audit_resync_parity(
    local_dir: Path,
    target_blobs: dict[str, str] | None = None,
    target_dir: Path | None = None,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    offline_fallback: bool = True,
    expected_additions: set[str] | None = None,
) -> dict[str, Any]:
    """Audit parity between local studysprint tree and a target source.

    Returns structured report with per-file status: identical, differs, missing_in_target,
    missing_in_local.
    `expected_additions`: files added as new tools or tests that may not exist in upstream
    timerloggedout-spec/studysprint before the Nov 3 sync, tracked explicitly.
    """
    local_blobs = scan_local_tree(local_dir)

    if target_blobs is None:
        if target_dir is not None and target_dir.exists():
            target_blobs = scan_local_tree(target_dir)
            source_desc = f"local-dir:{target_dir}"
        else:
            try:
                target_blobs = fetch_github_tree_blobs(repo=repo, branch=branch)
                source_desc = f"github:{repo}@{branch}"
            except Exception as e:
                if offline_fallback:
                    target_blobs = BASELINE_BLOBS
                    source_desc = "offline-baseline"
                else:
                    raise RuntimeError(f"Unable to reach remote and offline fallback disabled: {e}") from e
    else:
        source_desc = "provided-manifest"

    all_paths = sorted(set(local_blobs.keys()) | set(target_blobs.keys()))
    file_reports: list[dict[str, Any]] = []
    identical_count = 0
    differs_count = 0
    missing_in_target_count = 0
    missing_in_local_count = 0

    expected_additions = expected_additions or set()

    for path in all_paths:
        loc_sha = local_blobs.get(path)
        tgt_sha = target_blobs.get(path)

        if loc_sha is not None and tgt_sha is not None:
            if loc_sha == tgt_sha:
                status = "identical"
                identical_count += 1
            else:
                status = "differs"
                differs_count += 1
        elif loc_sha is not None and tgt_sha is None:
            status = "missing_in_target"
            missing_in_target_count += 1
        else:
            status = "missing_in_local"
            missing_in_local_count += 1

        file_reports.append({
            "path": path,
            "status": status,
            "local_sha": loc_sha,
            "target_sha": tgt_sha,
            "expected_addition": path in expected_additions,
        })

    # Total unhandled drift: files that differ or unexpected missing files
    unhandled_drift = (
        differs_count
        + missing_in_local_count
        + sum(1 for r in file_reports if r["status"] == "missing_in_target" and not r["expected_addition"])
    )

    return {
        "source": source_desc,
        "total_paths": len(all_paths),
        "identical": identical_count,
        "differs": differs_count,
        "missing_in_target": missing_in_target_count,
        "missing_in_local": missing_in_local_count,
        "drift_detected": unhandled_drift > 0,
        "files": file_reports,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="StudySprint Nov 3 Re-sync Parity Test")
    parser.add_argument("--local-dir", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Path to local studysprint app directory")
    parser.add_argument("--target-dir", type=Path, default=None,
                        help="Path to target local studysprint checkout directory (if any)")
    parser.add_argument("--repo", type=str, default=DEFAULT_REPO,
                        help="GitHub target repository (default: timerloggedout-spec/studysprint)")
    parser.add_argument("--branch", type=str, default=DEFAULT_BRANCH,
                        help="GitHub target branch (default: main)")
    parser.add_argument("--offline", action="store_true",
                        help="Force offline mode using baseline manifest")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--allow-unpushed-additions", action="store_true",
                        help="Allow newly developed tools/tests not yet pushed upstream")

    args = parser.parse_args(argv)

    target_blobs = BASELINE_BLOBS if args.offline else None
    expected_additions = {
        "tools/resync_parity.py",
        "tests/test_resync_parity.py",
    } if args.allow_unpushed_additions else set()

    try:
        report = audit_resync_parity(
            local_dir=args.local_dir,
            target_blobs=target_blobs,
            target_dir=args.target_dir,
            repo=args.repo,
            branch=args.branch,
            offline_fallback=True,
            expected_additions=expected_additions,
        )
    except Exception as e:
        sys.stderr.write(f"Error during parity audit: {e}\n")
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"=== StudySprint Parity Audit (target: {report['source']}) ===")
        print(f"Total files: {report['total_paths']}")
        print(f"  Identical:         {report['identical']}")
        print(f"  Differs:           {report['differs']}")
        print(f"  Missing in target: {report['missing_in_target']}")
        print(f"  Missing in local:  {report['missing_in_local']}")
        print("-" * 50)
        for f in report["files"]:
            status_str = f["status"].upper()
            if f.get("expected_addition"):
                status_str += " (EXPECTED ADDITION)"
            print(f"[{status_str:25}] {f['path']}")
        print("-" * 50)
        if report["drift_detected"]:
            print("RESULT: DRIFT DETECTED (exit 1)")
        else:
            print("RESULT: PARITY VERIFIED (exit 0)")

    return 1 if report["drift_detected"] else 0


if __name__ == "__main__":
    sys.exit(main())
