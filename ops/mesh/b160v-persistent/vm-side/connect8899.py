#!/usr/bin/env python3
"""SSH ProxyCommand: CONNECT through the local egress relay (127.0.0.1:8899).

Usage: ProxyCommand python3 ~/workspace/mesh-ssh/bin/connect8899.py %h %p

The relay accepts plain HTTP CONNECT (no auth on loopback) and reaches
public host:port targets. Tailnet targets go through tunnel-connect.py
(3130 selector) instead — this helper is for public endpoints only.
"""
import os, select, socket, sys

def main():
    host, port = sys.argv[1], int(sys.argv[2])
    s = socket.create_connection(("127.0.0.1", 8899), timeout=30)
    target = f"{host}:{port}"
    s.sendall(f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            sys.exit("relay closed during CONNECT")
        buf += chunk
    status = buf.split(b"\r\n")[0]
    if b" 200 " not in status:
        sys.exit(f"relay CONNECT refused: {status!r}")
    rest = buf.split(b"\r\n\r\n", 1)[1]
    if rest:
        os.write(1, rest)
    s.setblocking(False)
    fds = [s, sys.stdin.buffer]
    while True:
        r, _, _ = select.select(fds, [], [], 60)
        if not r:
            continue
        if s in r:
            data = s.recv(65536)
            if not data:
                return
            try:
                os.write(1, data)
            except OSError:
                return
        if sys.stdin.buffer in fds and sys.stdin.buffer in r:
            data = os.read(0, 65536)
            if not data:
                try: s.shutdown(socket.SHUT_WR)
                except OSError: pass
                fds.remove(sys.stdin.buffer)
            else:
                s.sendall(data)

if __name__ == "__main__":
    main()
