#!/usr/bin/env python3
"""Minimal stdlib WebSocket CDP probe for the Tier-1 engine proof.

Connects to an engine's webSocketDebuggerUrl, creates a target at the
fixture URL, waits for load, evaluates JS to extract the fixture's
JS-generated items, and prints ONE JSON object of evidence. No third-party
deps (the B160V law applies to tooling too: stdlib or it doesn't ship).

Usage: cdp_probe.py <cdp_http_base> <fixture_url>
Exit 0 when the evaluate round-trip succeeded, 1 otherwise (JSON either way).
"""
from __future__ import annotations

import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.parse
import urllib.request


def http_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


class WS:
    def __init__(self, url: str, timeout: float = 10.0):
        u = urllib.parse.urlparse(url)
        self.host = u.hostname or "127.0.0.1"
        self.port = u.port or 80
        self.path = u.path or "/"
        if u.query:
            self.path += "?" + u.query
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.buf = b""
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {self.path} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        while b"\r\n\r\n" not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("handshake closed")
            self.buf += chunk
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n", 1)[0] + b" ":
            raise ConnectionError(f"handshake refused: {head.splitlines()[0]!r}")

    def _read(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, payload: str) -> None:
        data = payload.encode()
        mask = os.urandom(4)
        header = bytearray([0x81])
        if len(data) < 126:
            header.append(0x80 | len(data))
        elif len(data) < 65536:
            header.append(0x80 | 126); header += struct.pack(">H", len(data))
        else:
            header.append(0x80 | 127); header += struct.pack(">Q", len(data))
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv(self) -> tuple[int, str]:
        while True:
            b0, b1 = self._read(2)
            fin, op = b0 & 0x80, b0 & 0x0F
            ln = b1 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._read(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._read(8))[0]
            payload = self._read(ln) if ln else b""
            if op == 9:  # ping -> pong
                self._pong(payload)
                continue
            if op in (1, 2, 0) and fin:
                return op, payload.decode("utf-8", "replace")

    def _pong(self, payload: bytes) -> None:
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes([0x8A, 0x80 | len(payload)]) + mask + masked)


class CDP:
    def __init__(self, ws: WS):
        self.ws = ws
        self.next_id = 0
        self.events: list[dict] = []

    def call(self, method: str, params: dict | None = None,
             session_id: str | None = None, timeout: float = 15.0) -> dict:
        self.next_id += 1
        msg: dict = {"id": self.next_id, "method": method, "params": params or {}}
        if session_id:
            msg["sessionId"] = session_id
        self.ws.send(json.dumps(msg))
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.sock.settimeout(max(0.1, deadline - time.time()))
            _, text = self.ws.recv()
            obj = json.loads(text)
            if obj.get("id") == self.next_id:
                return obj
            if "method" in obj:
                self.events.append(obj)
        raise TimeoutError(f"no reply for {method}")

    def wait_event(self, name: str, timeout: float = 10.0) -> dict | None:
        deadline = time.time() + timeout
        for ev in self.events:
            if ev.get("method") == name:
                return ev
        while time.time() < deadline:
            self.ws.sock.settimeout(max(0.1, deadline - time.time()))
            try:
                _, text = self.ws.recv()
            except (socket.timeout, TimeoutError):
                return None
            obj = json.loads(text)
            if "method" in obj:
                self.events.append(obj)
                if obj["method"] == name:
                    return obj
        return None


def main() -> int:
    base, fixture = sys.argv[1].rstrip("/"), sys.argv[2]
    out: dict = {"ws_connected": False, "target_created": False,
                 "navigated": False, "evaluate_ok": False}
    try:
        version = http_json(f"{base}/json/version")
        out["browser"] = version.get("Browser")
        ws = WS(version["webSocketDebuggerUrl"])
        out["ws_connected"] = True
        cdp = CDP(ws)
        v = cdp.call("Browser.getVersion")
        out["get_version_ok"] = "result" in v
        created = cdp.call("Target.createTarget", {"url": fixture})
        target_id = (created.get("result") or {}).get("targetId")
        out["target_created"] = bool(target_id)
        if not target_id:
            out["create_target_reply"] = created
            print(json.dumps(out)); return 1
        attached = cdp.call("Target.attachToTarget",
                            {"targetId": target_id, "flatten": True})
        session_id = (attached.get("result") or {}).get("sessionId")
        cdp.call("Page.enable", session_id=session_id)
        cdp.call("Runtime.enable", session_id=session_id)
        nav = cdp.call("Page.navigate", {"url": fixture}, session_id=session_id)
        out["navigated"] = "result" in nav and not nav["result"].get("errorText")
        cdp.wait_event("Page.loadEventFired", timeout=10)
        time.sleep(0.5)
        expr = ("JSON.stringify({status: document.getElementById('status')?.textContent, "
                "items: document.querySelectorAll('#items li').length, "
                "first: document.querySelector('#items li')?.textContent, "
                "embedded: document.getElementById('embedded')?.textContent?.trim()})")
        ev = cdp.call("Runtime.evaluate",
                      {"expression": expr, "returnByValue": True},
                      session_id=session_id)
        result = (ev.get("result") or {}).get("result") or {}
        if result.get("value"):
            out["evaluate_ok"] = True
            out["extracted"] = json.loads(result["value"])
        else:
            out["evaluate_reply"] = ev
        print(json.dumps(out))
        return 0 if out["evaluate_ok"] else 1
    except Exception as exc:  # evidence, not silence
        out["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(out))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
