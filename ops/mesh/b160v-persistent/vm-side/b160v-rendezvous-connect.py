#!/usr/bin/env python3
"""SSH ProxyCommand for Host b160v-persistent.

Reads the device's current tunnel endpoint from the rendezvous file
(mesh/b160v-endpoint.json in timerloggedout-spec/muse-vm-workspace-backup,
written by the device after every tunnel reconnect), then CONNECTs to it
through the local egress relay (127.0.0.1:8899) and bridges stdio.

Test override: B160V_ENDPOINT_JSON=/path/to/local.json
"""
import base64, json, os, select, socket, sys

sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github-pat/bin")

REPO = "timerloggedout-spec/muse-vm-workspace-backup"
PATH = "mesh/b160v-endpoint.json"

def load_endpoint():
    local = os.environ.get("B160V_ENDPOINT_JSON")
    if local:
        with open(local) as f:
            return json.load(f)
    import github_pat
    body = github_pat.call("GET", f"/repos/{REPO}/contents/{PATH}")
    raw = base64.b64decode(body["content"]).decode()
    return json.loads(raw)

def main():
    try:
        ep = load_endpoint()
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"b160v-rendezvous: cannot read endpoint file: {type(e).__name__}: {e}")
    host, port = ep.get("host"), ep.get("port")
    if not host or not port:
        sys.exit(f"b160v-rendezvous: no live endpoint published (status={ep.get('status')!r}, updated_at={ep.get('updated_at')!r}) — device-side install/loop not armed yet")
    sys.stderr.write(f"b160v-rendezvous: {host}:{port} (updated {ep.get('updated_at')}, source {ep.get('source')})\n")
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
