#!/usr/bin/env python3
"""MVT seeder — concurrent, per-provider banks, resumable.

Design:
  - Each provider gets its own bank: deepagent::mvt::<provider>::<comp_hash>
  - N concurrent workers POST single items (N bounded by provider RPM)
  - State per (provider, source): /tmp/mvt-state-<provider>-<source>.json
  - Reads active model from /tmp/hs-stack/active.json (rotator-driven)
  - Sources: FTS5 zip documents, deepseek conversations, pointers, codex

Usage:
  SEED_SOURCE=fts5 python3 mvt-seed.py
  SEED_SOURCE=conversations python3 mvt-seed.py
"""
import asyncio, json, os, sys, time, urllib.request, urllib.error, zipfile
from pathlib import Path

HS = os.environ.get("HINDSIGHT_BASE_URL", "http://localhost:8888").rstrip("/")
KEY = os.environ.get("HINDSIGHT_API_KEY", "")
BATCH_SIZE = int(os.environ.get("MVT_BATCH_SIZE", "8"))
BATCH_HARD_TIMEOUT = int(os.environ.get("MVT_BATCH_TIMEOUT", "90"))
LOG = Path("/tmp/mvt-seed.log")
ACTIVE = Path("/tmp/hs-stack/active.json")



def _active_role():
    """Read role from active.json (set by observatory/tournament) or default."""
    try:
        d = json.loads(ACTIVE.read_text())
        return d.get("role") or os.environ.get("MVT_ROLE") or "producer"
    except Exception:
        return os.environ.get("MVT_ROLE") or "producer"

def _active_model():
    try:
        return json.loads(ACTIVE.read_text()).get("model", "gemini-3.5-flash-lite")
    except Exception:
        return "gemini-3.5-flash-lite"

PROVIDERS = [
    {"name": "gemini",     "rpm": 15, "concurrency": 4, "pace": 3.0,
     "hs_url": "http://localhost:8888",
     "model_from_active": True},
    {"name": "openrouter", "rpm": 20, "concurrency": 4, "pace": 3.0,
     "hs_url": "http://localhost:8889",
     "model": "meta-llama/llama-3.3-70b-instruct:free"},
]

def log(m):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {m}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(line + "\n")

def state_path(provider, source):
    return Path(f"/tmp/mvt-state-{provider}-{source}.json")

def load_state(provider, source):
    p = state_path(provider, source)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}

def save_state(provider, source, s):
    state_path(provider, source).write_text(json.dumps(s))

# ── Sources ─────────────────────────────────────────────────────
def src_fts5_zip(zpath: Path):
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if "/documents/" not in name and not name.startswith("documents/"):
                continue
            try:
                d = json.loads(z.read(name))
            except Exception:
                continue
            txt = d.get("text") or d.get("content") or ""
            if len(txt) < 20:
                continue
            yield {
                "content": txt[:3500],
                "metadata": {
                    "origin": "fts5:" + zpath.name,
                    "key": str(d.get("key", ""))[:200],
                },
            }

def src_conversations(zpath: Path):
    with zipfile.ZipFile(zpath) as z:
        cands = [n for n in z.namelist() if n.endswith("conversations.json")]
        if not cands:
            return
        data = json.loads(z.read(cands[0]))
    convs = data if isinstance(data, list) else data.get("conversations", [])
    for cv in convs:
        mapping = cv.get("mapping") or {}
        parent_of = {
            k: (v.get("parent") if isinstance(v, dict) else None)
            for k, v in mapping.items()
        }
        roots = [k for k, p in parent_of.items() if p is None or p == "root"] or list(mapping.keys())[:1]
        title = cv.get("title") or "untitled"
        cid = cv.get("id") or ""

        def walk(k, d=0):
            if d > 500:
                return
            n = mapping.get(k)
            if not isinstance(n, dict):
                return
            m = n.get("message")
            if isinstance(m, dict):
                for i, fr in enumerate(m.get("fragments") or []):
                    if not isinstance(fr, dict):
                        continue
                    txt = fr.get("content") or ""
                    if len(txt) < 20:
                        continue
                    yield {
                        "content": f"[{title} {fr.get('type','')} #{i}]\n{txt[:1800]}",
                        "metadata": {
                            "origin": "conv",
                            "cid": str(cid),
                            "title": str(title)[:200],
                        },
                    }
            for c in (n.get("children") or []):
                yield from walk(c, d + 1)

        for r in roots:
            yield from walk(r)

def src_pointers(p: Path):
    try:
        d = json.loads(p.read_text())
    except Exception:
        return
    if not isinstance(d, dict):
        return
    for h, loc in d.items():
        sid = (loc or {}).get("session_id", "") if isinstance(loc, dict) else ""
        yield {
            "content": f"[Pointer] hash={h} session={sid}",
            "metadata": {"origin": "pointer", "hash": h, "session_id": str(sid)},
        }

def src_codex(p: Path):
    try:
        d = json.loads(p.read_text())
    except Exception:
        return
    items = (d.get("pointers") if isinstance(d, dict) else d) or []
    it = items.items() if isinstance(items, dict) else enumerate(items)
    for k, v in it:
        yield {
            "content": f"[Codex] {k}\n{json.dumps(v)[:1500]}",
            "metadata": {"origin": "codex", "key": str(k)},
        }

def _glob_first(pattern):
    hits = list(Path("/tmp").glob(pattern))
    return hits[0] if hits else None

def source_factory(name):
    if name == "fts5":
        z = _glob_first("bank-local-*.zip")
        return (lambda: src_fts5_zip(z)) if z else None
    if name == "conversations":
        z = _glob_first("deepseek_data-*.zip")
        return (lambda: src_conversations(z)) if z else None
    if name == "pointers":
        p = Path("/tmp/pointer_index.json")
        return (lambda: src_pointers(p)) if p.exists() else None
    if name == "codex":
        p = Path("/tmp/codex_index.json")
        return (lambda: src_codex(p)) if p.exists() else None
    return None

# ── Async post ──────────────────────────────────────────────────
async def post_batch(hs_url, bank, items, timeout=180):
    body = json.dumps({"items": items}).encode()
    loop = asyncio.get_running_loop()

    def _blocking():
        req = urllib.request.Request(
            f"{hs_url}/v1/default/banks/{bank}/memories",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {KEY}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return (r.status, "")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read()[:400].decode("utf-8", "replace")
            except Exception:
                pass
            return (e.code, body)
        except Exception as e:
            return (0, str(e)[:200])

    return await loop.run_in_executor(None, _blocking)

async def worker(name, hs_url, bank, queue, counters, pace):
    consec_quota = 0
    BATCH_WINDOW = 0.8  # seconds to wait for more items before posting

    while True:
        items = []
        try:
            first = await asyncio.wait_for(queue.get(), timeout=2.0)
        except asyncio.TimeoutError:
            continue
        if first is None:
            queue.task_done(); return
        items.append(first)

        deadline = time.monotonic() + BATCH_WINDOW
        while len(items) < BATCH_SIZE:
            remaining = deadline - time.monotonic()
            if remaining <= 0: break
            try:
                nxt = await asyncio.wait_for(queue.get(), timeout=remaining)
                if nxt is None:
                    queue.task_done(); break
                items.append(nxt)
            except asyncio.TimeoutError:
                break

        counters["batches"] = counters.get("batches", 0) + 1
        bnum = counters["batches"]
        if bnum <= 5 or bnum % 20 == 0:
            log(f"  [{name}] batch #{bnum} size={len(items)} posting...")
        _t0 = time.time()
        try:
            code, body = await asyncio.wait_for(
                post_batch(hs_url, bank, items),
                timeout=BATCH_HARD_TIMEOUT,
            )
        except asyncio.TimeoutError:
            code, body = 0, f"local timeout {BATCH_HARD_TIMEOUT}s"
        _dt = time.time() - _t0
        if bnum <= 5 or bnum % 20 == 0 or code != 200:
            log(f"  [{name}] batch #{bnum} -> HTTP {code} ({_dt:.1f}s)")
        for _ in items: queue.task_done()

        quota_in_body = ("RESOURCE_EXHAUSTED" in body
                         or '"code": 429' in body
                         or "quota" in body.lower())

        if code == 200:
            counters["ok"] += len(items)
            consec_quota = 0
        elif code == 429 or (code == 500 and quota_in_body):
            counters["429"] += len(items)
            consec_quota += 1
            log(f"  [{name}] quota (HTTP {code}) consec={consec_quota} batch={len(items)}")
            if consec_quota >= 5:
                log(f"  [{name}] ABORT lane: 5 consecutive quota errors")
                counters["abort"] = True
                while not queue.empty():
                    try:
                        queue.get_nowait(); queue.task_done()
                    except Exception:
                        break
                return
            await asyncio.sleep(20)
        else:
            counters["fail"] += len(items)
            if counters["fail"] % 20 == 0:
                log(f"  [{name}] HTTP {code} (fail={counters['fail']})")
        if code == 200 and counters["ok"] % 100 == 0:
            log(f"  [{name}] ok={counters['ok']} fail={counters['fail']} 429={counters['429']}")
        await asyncio.sleep(pace)

async def run_provider(provider, source):
    prov = provider["name"]
    comp_hash = "base"
    model = provider.get("model") or _active_model()
    role = provider.get("role") or _active_role()
    bank = f"deepagent::mvt::{prov}::{model}::{role}::{comp_hash}"
    state = load_state(prov, source)
    done = state.get("n_ok", 0)
    log(f"=== provider={prov} source={source} model={model} bank={bank} resumed_from={done} key={'SET' if KEY else 'MISSING'} ===")


    factory = source_factory(source)
    if factory is None:
        log(f"  source {source} unavailable (file not found in /tmp)")
        return

    q = asyncio.Queue(maxsize=provider["concurrency"] * 4)
    counters = {"ok": 0, "fail": 0, "429": 0, "abort": False}
    workers = [
        asyncio.create_task(worker(f"{prov}-{i}", provider["hs_url"], bank, q, counters, provider["pace"]))
        for i in range(provider["concurrency"])
    ]

    queued = 0
    _loop = asyncio.get_running_loop()
    _sentinel = object()

    def _next_item(gen):
        try:
            return next(gen)
        except StopIteration:
            return _sentinel

    gen = factory()

    async def _produce():
        q_n = 0
        while True:
            item = await _loop.run_in_executor(None, _next_item, gen)
            if item is _sentinel: break
            await q.put(item)
            q_n += 1
            if q_n % 50 == 0:
                log(f"  produced={q_n} qsize={q.qsize()}")
        for _ in workers: await q.put(None)
        log(f"  produced={q_n} total, sentinels sent")

    async def _watch():
        while not counters.get("abort"):
            await asyncio.sleep(1)
        while not q.empty():
            try:
                q.get_nowait(); q.task_done()
            except Exception:
                break

    producer = asyncio.create_task(_produce())
    watcher = asyncio.create_task(_watch())
    await asyncio.gather(producer, *workers, return_exceptions=True)
    watcher.cancel()

    log(f"  DONE {prov}/{source}: ok={counters['ok']} fail={counters['fail']} 429={counters['429']}")
    save_state(
        prov,
        source,
        {
            "n_ok": done + counters["ok"],
            "n_last_run_ok": counters["ok"],
            "n_fail": counters["fail"],
            "n_429": counters["429"],
            "ts": time.time(),
        },
    )

async def main():
    source = os.environ.get("SEED_SOURCE", "fts5")
    log(f"--- mvt-seed run source={source} model={_active_model()} ---")
    for p in PROVIDERS:
        try:
            await run_provider(p, source)
        except Exception as e:
            log(f"  provider {p['name']} crashed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
