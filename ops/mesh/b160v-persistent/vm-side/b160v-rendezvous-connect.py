#!/usr/bin/env python3
"""SSH ProxyCommand for Host b160v-persistent.

Reads the device's current tunnel endpoint from the rendezvous file
(mesh/b160v-endpoint.json in timerloggedout-spec/muse-vm-workspace-backup,
written by the device after every tunnel reconnect) and bridges stdio to
the device sshd through it. Two carrier shapes:

  proto "cloudflare": the endpoint host is a *.trycloudflare.com name.
      The device runs a Cloudflare quick tunnel to its sshd. We spawn
      `cloudflared access tcp` as a local listener (cloudflared's access
      dialer honors the proxy env, so it egresses via the sanctioned
      runtime proxy) and bridge stdio to that listener. cloudflared
      itself cannot ORIGINATE a tunnel from this VM — the runtime
      denies direct TCP — but the device side has ordinary egress.

  proto "tcp": the endpoint is a public host:port. CONNECT through the
      local egress relay (127.0.0.1:8899) and bridge stdio.

Test override: B160V_ENDPOINT_JSON=/path/to/local.json
cloudflared binary: $CLOUDFLARED_BIN or ~/workspace/tools/cloudflared/cloudflared
"""
import base64, json, os, select, socket, subprocess, sys, time

sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github-pat/bin")

REPO = "timerloggedout-spec/muse-vm-workspace-backup"
PATH = "mesh/b160v-endpoint.json"
CLOUDFLARED = os.environ.get(
    "CLOUDFLARED_BIN",
    os.path.expanduser("~/workspace/tools/cloudflared/cloudflared"))

def load_endpoint():
    local = os.environ.get("B160V_ENDPOINT_JSON")
    if local:
        with open(local) as f:
            return json.load(f)
    import github_pat
    body = github_pat.call("GET", f"/repos/{REPO}/contents/{PATH}")
    raw = base64.b64decode(body["content"]).decode()
    return json.loads(raw)

def bridge(sock):
    sock.setblocking(False)
    fds = [sock, sys.stdin.buffer]
    while True:
        r, _, _ = select.select(fds, [], [], 60)
        if not r:
            continue
        if sock in r:
            try:
                data = sock.recv(65536)
            except (ConnectionResetError, BrokenPipeError):
                return
            if not data:
                return
            try:
                os.write(1, data)
            except OSError:
                return
        if sys.stdin.buffer in fds and sys.stdin.buffer in r:
            data = os.read(0, 65536)
            if not data:
                try: sock.shutdown(socket.SHUT_WR)
                except OSError: pass
                fds.remove(sys.stdin.buffer)
            else:
                try: sock.sendall(data)
                except (ConnectionResetError, BrokenPipeError): return

def connect_via_relay(host, port):
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
    return s

def connect_via_cloudflared(hostname):
    if not os.path.exists(CLOUDFLARED):
        sys.exit(f"b160v-rendezvous: cloudflared binary missing at {CLOUDFLARED}")
    # Reserve an ephemeral loopback port, then hand it to cloudflared.
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    proc = subprocess.Popen(
        [CLOUDFLARED, "access", "tcp", "--hostname", hostname,
         "--url", f"127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 45
        while True:
            if proc.poll() is not None:
                sys.exit(f"b160v-rendezvous: cloudflared access exited rc={proc.returncode}")
            try:
                return socket.create_connection(("127.0.0.1", port), timeout=5), proc
            except OSError:
                if time.time() > deadline:
                    sys.exit("b160v-rendezvous: cloudflared access listener never came up")
                time.sleep(0.5)
    except BaseException:
        proc.terminate()
        raise

def main():
    try:
        ep = load_endpoint()
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"b160v-rendezvous: cannot read endpoint file: {type(e).__name__}: {e}")
    host, port, proto = ep.get("host"), ep.get("port"), ep.get("proto")
    if not host:
        sys.exit(f"b160v-rendezvous: no live endpoint published (status={ep.get('status')!r}, updated_at={ep.get('updated_at')!r}) — device-side install/loop not armed yet")
    sys.stderr.write(f"b160v-rendezvous: {host} proto={proto} (updated {ep.get('updated_at')}, source {ep.get('source')})\n")
    proc = None
    try:
        if proto == "cloudflare":
            sock, proc = connect_via_cloudflared(host)
        else:
            if not port:
                sys.exit(f"b160v-rendezvous: tcp endpoint without port: {ep!r}")
            sock = connect_via_relay(host, int(port))
        bridge(sock)
    finally:
        if proc is not None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill()

if __name__ == "__main__":
    main()
