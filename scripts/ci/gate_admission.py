"""Surface-aware admission for the Termux runtime smoke gate.

The repository gate remains universal. This module decides whether a change
touches the Termux execution surface and writes a stable GitHub Actions output.
All decisions use changed paths from the exact base/head pair; missing diff
evidence admits smoke as the safe default.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable

TERMUX_EXACT_PATHS = frozenset({
    ".github/workflows/termux-smoke.yml",
    "docs/ARCHW1Z-GATE.md",
    "docs/TERMUX-SMOKE.md",
    "docs/ops/SELF-IMPROVEMENT-MEMORY.schema.json",
    "scripts/agent_evolution/sim_memory.py",
    "scripts/ci/gate_admission.py",
    "scripts/ci/repo_gate.py",
    "scripts/ci/termux_smoke.py",
    "scripts/ci/validate_sim_memory.py",
    "tests/fixtures/sim-memory-smoke.jsonl",
    "tests/test_sim_memory.py",
    "tests/test_termux_smoke.py",
})

TERMUX_PREFIXES = (
    ".github/connectors/",
    "archwiz/",
    "bin/",
    "deepcli/",
    "deepcli-tui/",
    "integrations/ratatui-tokio-dashboard/",
    "multi-ai-cli/",
    "scripts/ci/termux_smoke/",
    "termux-multi-agent/",
)


def _normalize(path: str) -> str:
    normalized = str(path).replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def termux_smoke_required(paths: Iterable[str] | None) -> bool:
    """Return True when a changed path belongs to the Termux execution surface.

    Unknown path evidence returns True so the caller preserves the runtime check.
    """
    if paths is None:
        return True
    for raw_path in paths:
        path = _normalize(raw_path)
        if path in TERMUX_EXACT_PATHS:
            return True
        if any(path.startswith(prefix) for prefix in TERMUX_PREFIXES):
            return True
    return False


def decide_admission(event_name: str, paths: Iterable[str] | None) -> tuple[bool, str]:
    """Return (required, reason) for a GitHub event and its changed paths."""
    if event_name == "workflow_dispatch":
        return True, "manual workflow dispatch"
    if paths is None:
        return True, "diff unavailable; run smoke by default"
    if termux_smoke_required(paths):
        return True, "Termux execution surface changed"
    return False, "Termux surface unchanged"


def changed_paths(base_sha: str | None, head_sha: str | None,
                  repo_root: Path | None = None) -> list[str] | None:
    """Read changed paths from an exact base/head pair; return None on uncertainty."""
    if not base_sha or not head_sha or not base_sha.strip() or not head_sha.strip():
        return None
    if set(base_sha) == {"0"}:
        return None
    root = repo_root or Path(__file__).resolve().parents[2]
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--no-renames", base_sha, head_sha],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def admission_for_event(event_name: str, base_sha: str | None,
                        head_sha: str | None) -> tuple[bool, str]:
    if event_name == "workflow_dispatch":
        return decide_admission(event_name, [])
    paths = changed_paths(base_sha, head_sha)
    return decide_admission(event_name, paths)


def _write_output(path: str, required: bool, reason: str) -> None:
    safe_reason = reason.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"required={str(required).lower()}\n")
        handle.write(f"reason={safe_reason}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True)
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--github-output", default="")
    args = parser.parse_args()

    required, reason = admission_for_event(args.event, args.base, args.head)
    decision = "REQUIRED" if required else "SKIPPED"
    print(f"Termux smoke admission: {decision} — {reason}", flush=True)
    if args.github_output:
        _write_output(args.github_output, required, reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
