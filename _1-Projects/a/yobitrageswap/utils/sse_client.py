import time, sys, json
import urllib.parse, urllib.request

def stream_events(base_url: str, headers: dict):
    # SSE via query params because EventSource cannot set custom headers
    url = urllib.parse.urljoin(base_url, "/events/stream")
    q = urllib.parse.urlencode(headers)
    full = f"{url}?{q}"
    req = urllib.request.Request(full)
    with urllib.request.urlopen(req) as resp:
        buf = b""
        while True:
            chunk = resp.read(1024)
            if not chunk: break
            buf += chunk
            while b"\n\n" in buf:
                event, buf = buf.split(b"\n\n", 1)
                lines = event.decode().split("\n")
                etype = None
                data = ""
                for ln in lines:
                    if ln.startswith("event:"): etype = ln[6:].strip()
                    if ln.startswith("data:"): data += ln[5:].strip()
                if etype:
                    try:
                        payload = json.loads(data)
                    except Exception:
                        payload = {"raw": data}
                    print(json.dumps({"event": etype, "data": payload}))
                time.sleep(0.01)

if __name__ == "__main__":
    # Usage: python sse_client.py http://<ip>:8787 X-API-Key=<key> X-Timestamp=<ts> X-Signature=<sig>
    if len(sys.argv) < 5:
        print("Usage: sse_client.py BASE_URL key=val key=val key=val", file=sys.stderr); sys.exit(1)
    base = sys.argv[1]
    hdrs = dict(arg.split("=", 1) for arg in sys.argv[2:])
    stream_events(base, hdrs)
