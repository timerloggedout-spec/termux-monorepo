import os
import json
import pytest
import io
from unittest.mock import MagicMock, patch
import importlib.util

# Load bin/obsidian_server.py dynamically
spec = importlib.util.spec_from_file_location("obsidian_server", "bin/obsidian_server.py")
obsidian_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obsidian_server)

class DummyWFile:
    def __init__(self):
        self.data = b""
    def write(self, b):
        self.data += b

class DummyRFile:
    def __init__(self, data: bytes):
        self.stream = io.BytesIO(data)
    def read(self, n):
        return self.stream.read(n)

def create_handler(method="POST", headers=None, body=b""):
    handler = obsidian_server.RequestHandler.__new__(obsidian_server.RequestHandler)
    handler.headers = headers or {}
    handler.rfile = DummyRFile(body)
    handler.wfile = DummyWFile()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    return handler

def test_obsidian_server_unauthorized_token_missing(tmp_path, monkeypatch):
    token_file = tmp_path / "token.txt"
    monkeypatch.setattr(obsidian_server, "TOKEN_FILE", str(token_file))

    handler = create_handler()
    handler.do_POST()

    handler.send_response.assert_called_with(500)
    assert b"Server Error: Token missing" in handler.wfile.data

def test_obsidian_server_path_traversal_prevention(tmp_path, monkeypatch):
    token_file = tmp_path / "token.txt"
    token_file.write_text("secret_token")
    monkeypatch.setattr(obsidian_server, "TOKEN_FILE", str(token_file))

    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    # Payload targeting directory outside HOME (/etc)
    payload = json.dumps({"cmd": "pwd", "cwd": "/etc"}).encode("utf-8")
    headers = {
        "Authorization": "Bearer secret_token",
        "Content-Length": str(len(payload))
    }

    handler = create_handler(headers=headers, body=payload)

    mock_run_result = MagicMock()
    mock_run_result.stdout = f"/etc\n___OBSIDIAN_TERMUX_CWD___\n{fake_home}\n"
    mock_run_result.stderr = ""

    with patch("subprocess.run", return_value=mock_run_result) as mock_run:
        handler.do_POST()
        handler.send_response.assert_called_with(200)

        # Verify cwd was set to fake_home (HOME) rather than /etc
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["cwd"] == str(fake_home)
