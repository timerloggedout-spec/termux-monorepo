#!/usr/bin/env python3
"""On-codespace seeder. Reads local zips + sqlite, batches to localhost:8888.
No network round-trips — bank and seed run on the same host.
"""
import json, os, sqlite3, sys, time, urllib.request, urllib.error, zipfile
from pathlib import Path

HOME = Path.home()
HS = "http://localhost:8888"
BANK = "deepagent::termux-monorepo"
LOG = Path("/tmp/cs-seed.log")
STATE = Path("/tmp/cs-seed-state.json")
BATCH = int(os.environ.get("SEED_BATCH", "20"))
PACE = float(os.environ.get("SEED_PACE", "1"))

def log(m):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {m}"
    print(line, flush=True)
    with LOG.open("a") as f: f.write(line + "\n")

def state_load():
    if STATE.exists():
        try: return json.loads(STATE.read_text())
        except: return {}
    return {}

def state_save(s):
    STATE.write_text(json.dumps(s))

def post(items):
    body = json.dumps({"items": items}).encode()
    req = urllib.request.Request(
        f"{HS}/v1/default/banks/{BANK}/memories",
        data=body, method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        log(f"  post err {type(e).__name__}: {e}")
        return 0

def from_zip_documents(zpath: Path):
    """Read documents/*.json from a parity export zip."""
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if "/documents/" not in name and not name.startswith("documents/"):
                continue
            try:
                d = json.loads(z.read(name))
            except Exception:
                continue
            txt = d.get("text") or d.get("content") or ""
            if len(txt) < 20: continue
            yield {
                "content": txt[:3500],
                "metadata": {
                    "origin": "zip:" + zpath.name,
                    "doc_id": str(d.get("id",""))[:64],
                    "src": str(d.get("source",""))[:40],
                    "key": str(d.get("key",""))[:200],
                }
            }

def from_conversations(zpath: Path):
    """DeepSeek export format: list of {title, mapping:{...fragments...}}."""
    with zipfile.ZipFile(zpath) as z:
        # find conversations.json in the archive
        cands = [n for n in z.namelist() if n.endswith("conversations.json")]
        if not cands:
            log(f"  no conversations.json in {zpath.name}")
            return
        data = json.loads(z.read(cands[0]))
    convs = data if isinstance(data, list) else data.get("conversations", [])
    log(f"  {zpath.name}: {len(convs)} conversations")
    for cv in convs:
        mapping = cv.get("mapping") or {}
        parent_of = {k:(v.get("parent") if isinstance(v,dict) else None) for k,v in mapping.items()}
        roots = [k for k,p in parent_of.items() if p is None or p=="root"] or list(mapping.keys())[:1]
        title = cv.get("title") or "untitled"
        cid = cv.get("id") or ""
        when = cv.get("inserted_at") or ""
        def walk(k, d=0):
            if d > 500: return
            n = mapping.get(k)
            if not isinstance(n, dict): return
            m = n.get("message")
            if isinstance(m, dict):
                for i, fr in enumerate(m.get("fragments") or []):
                    if not isinstance(fr, dict): continue
                    txt = fr.get("content") or ""
                    if len(txt) < 20: continue
                    yield {
                        "content": f"[{title} {fr.get('type','')} #{i}]\n{txt[:1800]}",
                        "metadata": {
                            "origin": "conversations.json",
                            "conversation_id": str(cid),
                            "title": str(title)[:200],
                            "when": str(when),
                            "frag_type": str(fr.get("type","")),
                        }
                    }
            for c in (n.get("children") or []): yield from walk(c, d+1)
        for r in roots:
            yield from walk(r)

def iter_sources():
    # prefer: local FTS5 zip, then conversations
    zips = sorted(Path("/tmp").glob("bank-local-*.zip")) + \
           sorted(Path("/tmp").glob("deepseek_data-*.zip"))
    for z in zips:
        if z.name.startswith("bank-local"):
            log(f"  source: {z.name} (parity documents)")
            yield from from_zip_documents(z)
        else:
            log(f"  source: {z.name} (conversations)")
            yield from from_conversations(z)

def main():
    if not STATE.exists():
        STATE.write_text(json.dumps({"n_ok":0, "n_fail":0, "batches":0}))
    s = state_load()
    n_ok = s.get("n_ok", 0)
    n_fail = s.get("n_fail", 0)
    batches = s.get("batches", 0)
    buf = []
    t0 = time.time()

    for item in iter_sources():
        buf.append(item)
        if len(buf) >= BATCH:
            code = post(buf)
            batches += 1
            if code == 200:
                n_ok += len(buf)
                if batches % 5 == 0:
                    log(f"  batch {batches} ok  total={n_ok}  elapsed={int(time.time()-t0)}s")
            else:
                n_fail += len(buf)
                log(f"  batch {batches} HTTP {code}")
                if code in (429,500,502,503):
                    log("  backoff 45s"); time.sleep(45)
            buf = []
            state_save({"n_ok":n_ok,"n_fail":n_fail,"batches":batches,"ts":time.time()})
            time.sleep(PACE)
    if buf:
        code = post(buf)
        batches += 1
        if code == 200: n_ok += len(buf)
    log(f"  DONE ok={n_ok} fail={n_fail} batches={batches}")
    state_save({"n_ok":n_ok,"n_fail":n_fail,"batches":batches,"done":True})

if __name__ == "__main__":
    main()
