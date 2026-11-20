#!/usr/bin/env python3
"""Lightweight CEDARscript bridge – no persistent server, stdin/stdout MCP."""
import subprocess, json, sys

def cedar_validate(code: str, schema: str = "{}") -> str:
    res = subprocess.run(
        ["cedar", "validate", "--schema", schema, "-p", "-"],
        input=code.encode(), capture_output=True, text=True, timeout=10
    )
    return res.stdout + res.stderr

def cedar_eval(code: str, schema: str, input_json: str) -> str:
    res = subprocess.run(
        ["cedar", "evaluate", "--schema", schema, "--input", input_json, "-p", "-"],
        input=code.encode(), capture_output=True, text=True, timeout=10
    )
    return res.stdout + res.stderr

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cedar_bridge.py validate|eval [args...]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "validate":
        code = sys.stdin.read() if len(sys.argv) == 2 else sys.argv[2]
        print(cedar_validate(code))
    elif cmd == "eval":
        code = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        schema = sys.argv[3] if len(sys.argv) > 3 else "{}"
        inp = sys.argv[4] if len(sys.argv) > 4 else "{}"
        print(cedar_eval(code, schema, inp))
