#!/usr/bin/env python3
"""Log every tool execution: timestamp, tool, exit code, output snippet."""
import json, sys, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

LOG_FILE = Path.home() / 'workspace/llm_map/tool_runs.jsonl'

def log_run(tool_name, args, exit_code, stdout_snippet, stderr_snippet):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "args": args,
        "exit_code": exit_code,
        "stdout": stdout_snippet[:200],
        "stderr": stderr_snippet[:200]
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: tool_logger.py <command> [args...]")
        sys.exit(1)
    cmd = sys.argv[1:]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_run(cmd[0], cmd[1:], result.returncode, result.stdout, result.stderr)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
