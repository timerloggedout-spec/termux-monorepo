#!/usr/bin/env python3
"""Bounded no-auth inference smoke over the harvested g4f-working catalog.

Manual/dispatch only. Reads data/g4f-working/providers.json working_models
entries, sends ONE synthetic completion per (provider, model) via the g4f
library, and writes a sanitized receipt (schema g4f-inference-smoke/v1):
provider/model/ok/latency/error-class only -- response bodies are never
persisted. Not the scheduled availability probe (which stays catalog-only),
never changes routing or production admission, no credentials (no-auth
providers only), no retries, no paid fallback.
"""
import argparse, concurrent.futures, datetime as dt, json, os, sys, time
from pathlib import Path

PROMPT = "Reply with exactly: OK"

def probe(entry):
    import g4f
    from g4f.client import Client
    provider_id, model = entry
    started = time.time()
    result = {"provider": provider_id, "model": model, "inference_ok": False,
              "latency_s": None, "error": None}
    try:
        provider = None
        for name in dir(g4f.Provider):
            if name.lower() == provider_id.lower():
                provider = getattr(g4f.Provider, name); break
        kwargs = {"model": model, "messages": [{"role": "user", "content": PROMPT}]}
        if provider is not None:
            kwargs["provider"] = provider
        proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
        if proxy:
            kwargs["proxy"] = proxy
        resp = Client().chat.completions.create(**kwargs)
        text = resp.choices[0].message.content if resp and resp.choices else ""
        result["inference_ok"] = bool(text and text.strip())
        if not result["inference_ok"]:
            result["error"] = "empty_response"
    except Exception as exc:  # error class only, never raw text
        result["error"] = type(exc).__name__
    result["latency_s"] = round(time.time() - started, 2)
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="data/g4f-working/providers.json")
    ap.add_argument("--source", choices=["catalog", "working", "universe"], default="catalog",
                    help="catalog = fork tester-working entries; working = verified endpoints file; universe = full pair universe")
    ap.add_argument("--working", default="data/g4f-working/working-endpoints.json")
    ap.add_argument("--universe", default="data/g4f-working/universe.json")
    ap.add_argument("--output", default="g4f-inference-smoke.json")
    ap.add_argument("--limit", type=int, default=100, help="max completions this run")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=90, help="per-call timeout seconds")
    ap.add_argument("--deadline", type=int, default=1500, help="global wall-clock deadline seconds; stragglers recorded as DeadlineExceeded and the receipt still writes")
    args = ap.parse_args()

    if args.source == "working":
        doc = json.loads(Path(args.working).read_text())
        entries = [(e["provider"], e["model"]) for e in doc["endpoints"]]
    elif args.source == "universe":
        doc = json.loads(Path(args.universe).read_text())
        entries = [(p["provider"], p["model"]) for p in doc["pairs"]]
    else:
        catalog = json.loads(Path(args.catalog).read_text())
        entries = []
        for p in catalog["providers"]:
            for wm in p.get("working_models", []):
                entries.append((p["id"], wm["model"]))
    entries = entries[: args.limit]

    results = []
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)
    futures = {ex.submit(probe, e): e for e in entries}
    done, not_done = concurrent.futures.wait(futures, timeout=args.deadline)
    for fut in done:
        try:
            results.append(fut.result())
        except Exception as exc:
            prov, model = futures[fut]
            results.append({"provider": prov, "model": model, "inference_ok": False,
                            "latency_s": None, "error": type(exc).__name__})
    for fut in not_done:
        prov, model = futures[fut]
        results.append({"provider": prov, "model": model, "inference_ok": False,
                        "latency_s": None, "error": "DeadlineExceeded"})
        fut.cancel()
    ex.shutdown(wait=False, cancel_futures=True)
    results.sort(key=lambda r: (r["provider"], r["model"]))
    receipt = {
        "schema": "g4f-inference-smoke/v1",
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": args.source,
        "attempted": len(results),
        "inference_ok": sum(1 for r in results if r["inference_ok"]),
        "providers_ok": sorted({r["provider"] for r in results if r["inference_ok"]}),
        "results": results,
        "production_admission_changed": False,
        "paid_fallback_allowed": False,
    }
    Path(args.output).write_text(json.dumps(receipt, indent=1) + "\n")
    print(json.dumps({k: receipt[k] for k in ("attempted", "inference_ok", "providers_ok")}, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
