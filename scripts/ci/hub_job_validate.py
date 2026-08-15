#!/usr/bin/env python3
"""Run the dependency-free Termux hub protocol test suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    command = [sys.executable, "-m", "unittest", "tests.hub_mcp.test_protocol", "-v"]
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
