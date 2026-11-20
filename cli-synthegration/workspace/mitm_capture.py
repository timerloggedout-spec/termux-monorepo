"""mitmproxy addon – log DeepSeek API requests to sniffer_capture.log"""
import json
from pathlib import Path
LOG = Path.home() / "cli-synthegration" / "sniffer_capture.log"

def request(flow):
    url = flow.request.pretty_url
    if "chat.deepseek.com/api" not in url:
        return
    entry = f"\n=== {flow.request.method} {url} ==="
    for k, v in flow.request.headers.items():
        if any(t in k.lower() for t in ("client","app","version","auth","expert","content","cookie","x-ds","pow")):
            entry += f"\n  {k}: {v}"
    body = flow.request.get_text()
    if body and len(body) < 5000:
        entry += f"\n  BODY: {body[:2000]}"
    print(entry)
    with open(LOG, "a") as f:
        f.write(entry + "\n")
