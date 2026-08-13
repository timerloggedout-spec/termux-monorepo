import os
import sys
import json
import subprocess
import time
from pathlib import Path
import pytest

def test_cedar_mcp_server_flow(tmp_path):
    server_path = Path(__file__).parent.parent / "termux-multi-agent" / "cedar-mcp-server.js"
    assert server_path.exists(), f"Server not found at {server_path}"

    # Spawn MCP server process
    proc = subprocess.Popen(
        ["node", str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # 1. Test tools/list
        req_list = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        proc.stdin.write(json.dumps(req_list) + "\n")
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        assert response_line, "No response from MCP server"
        res_list = json.loads(response_line)
        assert res_list["id"] == 1
        assert "result" in res_list
        assert "tools" in res_list["result"]
        tools = res_list["result"]["tools"]
        assert len(tools) == 2
        assert tools[0]["name"] == "cedar_validate"
        assert tools[1]["name"] == "cedar_eval"

        # 2. Test tools/call with cedar_eval (normal error handling, e.g. ENOENT or file not found)
        req_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "cedar_eval",
                "arguments": {
                    "schema": "test_schema.cedar",
                    "input": "test_input.json"
                }
            }
        }
        proc.stdin.write(json.dumps(req_call) + "\n")
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        assert response_line, "No response from MCP server for tool call"
        res_call = json.loads(response_line)
        assert res_call["id"] == 2
        assert "result" in res_call
        text_out = res_call["result"]["content"][0]["text"]
        # Since 'cedar' is not installed in the test env, it should return spawn ENOENT or similar message
        # without crashing the process.
        assert "ENOENT" in text_out or "spawn" in text_out or "cedar" in text_out

        # 3. Test Command Injection Mitigation
        # Create a trigger file path that should NOT be created or touched
        canary_file = tmp_path / "should_not_exist_canary"
        assert not canary_file.exists()

        # If we had a command injection vulnerability, this payload would touch/create the file:
        # e.g., "; touch <canary_file>"
        injection_payload = f"; touch {canary_file}"

        req_inject = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "cedar_eval",
                "arguments": {
                    "schema": injection_payload,
                    "input": "test_input.json"
                }
            }
        }
        proc.stdin.write(json.dumps(req_inject) + "\n")
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        assert response_line, "No response from MCP server for injected tool call"
        res_inject = json.loads(response_line)
        assert res_inject["id"] == 3

        # Wait a small moment to ensure no asynchronous execution touched the file
        time.sleep(0.1)
        assert not canary_file.exists(), "CRITICAL SECURITY VULNERABILITY: Command injection payload was executed!"

        # 4. Ensure server is still alive and responsive
        req_alive = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/list",
            "params": {}
        }
        proc.stdin.write(json.dumps(req_alive) + "\n")
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        assert response_line, "Server died after handling injection attempt"
        res_alive = json.loads(response_line)
        assert res_alive["id"] == 4

    finally:
        proc.terminate()
        proc.wait()
