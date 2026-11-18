#!/usr/bin/env python3
"""QUE inference endpoint availability probe.

Per endpoint from ``scripts/provider_model_catalog.ENDPOINTS``:

* classify the completion route (openai-compat, native gemini, catalog-only);
* list models + settings (context length, pricing -> free flag);
* capture provider-declared limits ("theirs") from rate-limit headers or a
  documented snapshot, and our consumed calls ("ours") from the inference
  availability ledger (PR #5600) or this probe's own log;
* run AT MOST ONE 1-token completion (max_tokens=1) against a model classified
  free; skip with ``skipped:no_free_model`` / ``skipped:no_secret`` otherwise;
* compute ``safe_parallel_slots``.

Output carries presence booleans only: secret values and keys stay out of every
record, log line, and error string.

Modes:
  matrix     print the endpoint matrix JSON for the workflow setup job
  probe      probe one endpoint, write a raw record JSON
  aggregate  merge raw records -> ops/inference/endpoint-availability.json and
             append ops/inference/endpoint-probe-log.jsonl
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

try:
    from scripts import provider_catalog_protocols as pcp  # type: ignore
    from scripts import provider_extension_catalogs as pec  # type: ignore
    from scripts import provider_model_catalog as pmc  # type: ignore
except ImportError:  # pragma: no cover - script execution fallback
    import provider_catalog_protocols as pcp  # type: ignore
    import provider_extension_catalogs as pec  # type: ignore
    import provider_model_catalog as pmc  # type: ignore

SCHEMA = "inference-endpoint-availability/v1"
UA = "termux-monorepo-endpoint-probe/1"
SAFETY = 0.5
DEFAULT_DOE_CALLS_PER_SLOT_DAY = 50
MAX_COMPLETIONS_PER_ENDPOINT = 1
MAX_FREE_MODELS_LISTED = 25
HEADER_PREFIXES = pmc.HEADER_PREFIXES
HEADER_EXACT = pmc.HEADER_EXACT

# Providers whose API keys sit on a documented free tier (upgrade is an explicit
# account action). Models from these count as free for the 1-token check.
# Gemini/Mistral/SambaNova stay off this list: a billing-enabled key would charge.
DOCUMENTED_FREE_TIER = {
    "groq": "https://console.groq.com/docs/rate-limits",
    "cerebras": "https://inference-docs.cerebras.ai/support/rate-limits",
    "llm7": "https://llm7.io",
}
# Documented free-tier limit snapshots ("theirs" when headers are silent).
DOCUMENTED_LIMITS = {
    "openrouter": {"rpm": 20, "rpd": 50, "source": "https://openrouter.ai/docs/api-reference/limits", "scope": ":free models, account without credits"},
    "groq": {"rpm": 30, "rpd": 14400, "source": "https://console.groq.com/docs/rate-limits", "scope": "llama-3.1-8b-instant free tier"},
    "cerebras": {"rpm": 30, "rpd": 14400, "source": "https://inference-docs.cerebras.ai/support/rate-limits", "scope": "free tier"},
}
PREFERRED_MODELS = {
    "groq": ("llama-3.1-8b-instant",),
    "cerebras": ("llama3.1-8b",),
}
SAFE_ERROR = re.compile(r"http_status_[1-5][0-9][0-9]|response_too_large|invalid_json|invalid_response_shape|invalid_pagination|invalid_model|timeout|url_error|unsupported_provider|invalid_account_id")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- routes
def route_class(endpoint: str) -> dict[str, Any]:
    url = pmc.ENDPOINTS.get(endpoint, "")
    if endpoint == "gemini":
        return {"route_class": "native:gemini.generateContent",
                "completion_url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                "auth_header": "x-goog-api-key"}
    if endpoint in pcp.PROVIDERS:
        return {"route_class": "catalog_only", "completion_url": None, "auth_header": "Authorization"}
    if url.endswith("/models"):
        return {"route_class": "openai-compat:/v1/chat/completions",
                "completion_url": url[: -len("/models")] + "/chat/completions",
                "auth_header": "Authorization"}
    return {"route_class": "catalog_only", "completion_url": None, "auth_header": "Authorization"}


def secret_names(endpoint: str) -> list[str]:
    names = pmc.RESOLVE_SECRET_NAMES.get(endpoint) or (pmc.SECRETS.get(endpoint),)
    return [n for n in names if n]


def build_matrix() -> list[dict[str, Any]]:
    rows = []
    for endpoint in sorted(pmc.ENDPOINTS):
        names = secret_names(endpoint) + ["", "", "", ""]
        rows.append({"endpoint": endpoint, "secret": names[0], "alias1": names[1],
                     "alias2": names[2], "alias3": names[3],
                     "public_catalog": endpoint in pmc.PUBLIC_CATALOGS})
    return rows


# --------------------------------------------------------------------------- models
def is_free(endpoint: str, row: dict[str, Any]) -> tuple[bool, str | None]:
    if endpoint == "openrouter":
        return (bool(row.get("free_suffix")), "openrouter:free_suffix" if row.get("free_suffix") else None)
    if row.get("pricing_classification") == "free_zero_price":
        return True, "catalog_zero_price"
    if row.get("access_classification") == "free_trial":
        return True, "documented_free_trial"
    if endpoint in DOCUMENTED_FREE_TIER:
        return True, "documented_free_tier"
    return False, None


def summarize_models(endpoint: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    free = []
    for row in rows:
        ok, basis = is_free(endpoint, row)
        if ok:
            free.append({"id": row.get("id"), "context_length": row.get("context_length"),
                         "max_output_tokens": row.get("max_output_tokens"),
                         "pricing_classification": row.get("pricing_classification"),
                         "free_basis": basis})
    free.sort(key=lambda m: str(m["id"]))
    return {"model_count": len(rows), "free_model_count": len(free), "free_models": free}


def pick_free_model(endpoint: str, free_models: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not free_models:
        return None
    by_id = {m["id"]: m for m in free_models}
    for pref in PREFERRED_MODELS.get(endpoint, ()):
        if pref in by_id:
            return by_id[pref]
    # smallest declared context first (cheap, fast), then id
    return sorted(free_models, key=lambda m: (m.get("context_length") or 10**12, str(m["id"])))[0]


# --------------------------------------------------------------------------- http
def filter_headers(headers: dict[str, Any]) -> dict[str, str]:
    out = {}
    for key, value in (headers or {}).items():
        k = str(key).lower()
        if k.startswith(HEADER_PREFIXES) or k in HEADER_EXACT:
            out[k] = str(value)[:120]
    return out


def default_post(url: str, headers: dict[str, str], body: dict[str, Any]) -> tuple[int, dict[str, str]]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read(256 * 1024)
            return resp.status, dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()) if exc.headers else {}
    except TimeoutError:
        raise ValueError("timeout") from None
    except urllib.error.URLError:
        raise ValueError("url_error") from None


class CallBudget:
    """Hard cap: MAX_COMPLETIONS_PER_ENDPOINT completion calls per endpoint per run."""

    def __init__(self, cap: int = MAX_COMPLETIONS_PER_ENDPOINT):
        self.cap = cap
        self.used: dict[str, int] = {}

    def take(self, endpoint: str) -> bool:
        if self.used.get(endpoint, 0) >= self.cap:
            return False
        self.used[endpoint] = self.used.get(endpoint, 0) + 1
        return True


def completion_check(endpoint: str, model: str, token: str, budget: CallBudget,
                     post: Callable = default_post) -> dict[str, Any]:
    route = route_class(endpoint)
    if not route["completion_url"]:
        return {"status": "skipped:no_completion_route", "calls": 0}
    if not budget.take(endpoint):
        return {"status": "skipped:call_cap", "calls": 0}
    if endpoint == "gemini":
        url = route["completion_url"].format(model=model)
        headers = {"x-goog-api-key": token}
        body = {"contents": [{"parts": [{"text": "hi"}]}], "generationConfig": {"maxOutputTokens": 1}}
    else:
        url = route["completion_url"]
        headers = {"Authorization": f"Bearer {token}"}
        body = {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
    headers.update({"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    started = time.monotonic()
    try:
        status, resp_headers = post(url, headers, body)
    except Exception as exc:  # sanitized: provider text never echoed
        msg = str(exc) if SAFE_ERROR.fullmatch(str(exc)) else "request_failed"
        return {"status": "failed", "error": msg, "calls": 1,
                "latency_ms": int((time.monotonic() - started) * 1000), "headers": {}}
    result = {"status": "ok" if 200 <= status < 300 else "failed", "http_status": status, "calls": 1,
              "latency_ms": int((time.monotonic() - started) * 1000), "headers": filter_headers(resp_headers)}
    if result["status"] == "failed":
        result["error"] = f"http_status_{status}"
    return result


# --------------------------------------------------------------------------- limits
def _num(value: Any) -> float | None:
    try:
        n = float(str(value).split(",")[0].strip())
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) and n >= 0 else None


def declared_limits(endpoint: str, headers: dict[str, str]) -> dict[str, Any]:
    """'theirs': provider-declared limits from headers, else documented snapshot."""
    h = {k.lower(): v for k, v in (headers or {}).items()}
    out: dict[str, Any] = {"rpm": None, "rpd": None, "remaining_minute": None, "remaining_day": None,
                           "retry_after_s": _num(h.get("retry-after")), "source": None}
    for key, val in h.items():
        n = _num(val)
        if n is None or "token" in key:
            continue
        if key.startswith("x-ratelimit-limit-requests-minute") or key == "x-ratelimit-limit-rpm":
            out["rpm"] = n
        elif key.startswith("x-ratelimit-limit-requests-day") or key == "x-ratelimit-limit-rpd":
            out["rpd"] = n
        elif key.startswith("x-ratelimit-remaining-requests-minute"):
            out["remaining_minute"] = n
        elif key.startswith("x-ratelimit-remaining-requests-day"):
            out["remaining_day"] = n
        elif key == "x-ratelimit-limit-requests":  # groq/openai: per-day request ceiling
            out["rpd"] = out["rpd"] if out["rpd"] is not None else n
        elif key == "x-ratelimit-remaining-requests":
            out["remaining_day"] = out["remaining_day"] if out["remaining_day"] is not None else n
    if any(out[k] is not None for k in ("rpm", "rpd", "remaining_minute", "remaining_day")):
        out["source"] = "response_headers"
    doc = DOCUMENTED_LIMITS.get(endpoint)
    if doc:
        if out["rpm"] is None:
            out["rpm"] = doc["rpm"]
        if out["rpd"] is None:
            out["rpd"] = doc["rpd"]
        out["source"] = out["source"] + "+docs" if out["source"] else "docs_snapshot"
        out["docs_source"] = doc["source"]
        out["docs_scope"] = doc["scope"]
    return out


def safe_parallel_slots(theirs: dict[str, Any], ours_24h: int,
                        doe_calls_per_slot: int = DEFAULT_DOE_CALLS_PER_SLOT_DAY,
                        safety: float = SAFETY) -> dict[str, Any]:
    """floor(min(RPM/concurrency headroom, remaining daily / expected DoE calls) x safety)."""
    rpm_headroom = theirs.get("remaining_minute")
    if rpm_headroom is None:
        rpm_headroom = theirs.get("rpm")
    remaining_day = theirs.get("remaining_day")
    if remaining_day is None and theirs.get("rpd") is not None:
        remaining_day = max(0.0, float(theirs["rpd"]) - ours_24h)
    day_slots = remaining_day / doe_calls_per_slot if remaining_day is not None and doe_calls_per_slot > 0 else None
    terms = [t for t in (rpm_headroom, day_slots) if t is not None]
    if not terms:
        return {"safe_parallel_slots": 0, "basis": "no_declared_limits", "rpm_headroom": None,
                "remaining_day": None, "day_slots": None}
    return {"safe_parallel_slots": int(math.floor(min(terms) * safety)), "basis": "min(rpm,day/doe)*safety",
            "rpm_headroom": rpm_headroom, "remaining_day": remaining_day,
            "day_slots": round(day_slots, 3) if day_slots is not None else None}


# --------------------------------------------------------------------------- ours
LEDGER_PROVIDER_ALIASES = {"google": "gemini", "hf": "huggingface"}


def ours_from_ledger(ledger: dict[str, Any] | None) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in (ledger or {}).get("endpoints", []) or []:
        prov = LEDGER_PROVIDER_ALIASES.get(row.get("provider"), row.get("provider"))
        n = row.get("measured_24h")
        if isinstance(prov, str) and isinstance(n, int):
            out[prov] = max(out.get(prov, 0), n)  # measured_scope is provider-shared
    return out


def ours_from_log(lines: list[str], now: dt.datetime) -> dict[str, int]:
    out: dict[str, int] = {}
    cutoff = now - dt.timedelta(hours=24)
    for line in lines:
        try:
            rec = json.loads(line)
            ts = dt.datetime.fromisoformat(rec["observed_at"].replace("Z", "+00:00"))
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        if ts >= cutoff:
            out[rec.get("endpoint")] = out.get(rec.get("endpoint"), 0) + int(rec.get("calls", 0) or 0)
    return out


# --------------------------------------------------------------------------- probe
def load_catalog(endpoint: str, token: str | None, cache_dir: str | None,
                 poll: Callable = pmc.poll) -> tuple[list[dict], dict, str]:
    day = dt.date.today().isoformat()
    path = Path(cache_dir) / f"{endpoint}-{day}.json" if cache_dir else None
    if path and path.exists():
        cached = json.loads(path.read_text())
        return cached["models"], cached.get("headers", {}), "hit"
    rows, headers = poll(endpoint, token)
    headers = filter_headers(headers)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        slim = [{k: r.get(k) for k in ("id", "context_length", "max_output_tokens", "pricing_classification",
                                       "access_classification", "free_suffix")} for r in rows]
        path.write_text(json.dumps({"models": slim, "headers": headers}))
    return rows, headers, "miss"


def probe_endpoint(endpoint: str, token: str | None, *, budget: CallBudget | None = None,
                   cache_dir: str | None = None, poll: Callable = pmc.poll,
                   post: Callable = default_post) -> dict[str, Any]:
    budget = budget or CallBudget()
    route = route_class(endpoint)
    rec: dict[str, Any] = {"endpoint": endpoint, "observed_at": now_iso(), **{k: route[k] for k in ("route_class",)},
                           "secret_present": bool(token), "public_catalog": endpoint in pmc.PUBLIC_CATALOGS,
                           "secret_env": secret_names(endpoint)[0] if secret_names(endpoint) else None,
                           "catalog": {"status": "skipped"}, "check": {"status": "skipped:no_secret", "calls": 0}}
    if endpoint not in pmc.ENDPOINTS:
        rec["catalog"] = {"status": "failed", "error": "unsupported_provider"}
        return rec
    catalog_headers: dict[str, str] = {}
    free_models: list[dict] = []
    if token or endpoint in pmc.PUBLIC_CATALOGS:
        try:
            rows, catalog_headers, cache = load_catalog(endpoint, token, cache_dir, poll)
            summary = summarize_models(endpoint, rows)
            free_models = summary["free_models"]
            rec["catalog"] = {"status": "ok", "cache": cache, "model_count": summary["model_count"],
                              "free_model_count": summary["free_model_count"],
                              "free_models": free_models[:MAX_FREE_MODELS_LISTED], "headers": catalog_headers}
        except Exception as exc:
            msg = str(exc) if SAFE_ERROR.fullmatch(str(exc)) else "request_failed"
            rec["catalog"] = {"status": "failed", "error": msg}
    if not token:
        rec["check"] = {"status": "skipped:no_secret", "calls": 0}
    elif not free_models:
        rec["check"] = {"status": "skipped:no_free_model", "calls": 0}
    else:
        model = pick_free_model(endpoint, free_models)
        rec["check"] = {"model": model["id"], "free_basis": model["free_basis"],
                        **completion_check(endpoint, model["id"], token, budget, post)}
    merged = dict(catalog_headers)
    merged.update(rec["check"].get("headers", {}))
    rec["theirs"] = declared_limits(endpoint, merged)
    rec["calls"] = rec["check"].get("calls", 0)
    return rec


# --------------------------------------------------------------------------- aggregate
def aggregate(records: list[dict], ledger: dict | None, log_lines: list[str],
              doe_calls_per_slot: int = DEFAULT_DOE_CALLS_PER_SLOT_DAY,
              run_meta: dict | None = None) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc)
    ledger_ours = ours_from_ledger(ledger)
    log_ours = ours_from_log(log_lines, now)
    out_rows, total, counts = [], 0, {"ok": 0, "skipped": 0, "failed": 0}
    cache_stats = {"catalog_hit": 0, "catalog_miss": 0, "pip_hit": None, "jobs": []}
    for rec in sorted(records, key=lambda r: r.get("endpoint", "")):
        ep = rec.get("endpoint")
        source = "inference-ledger" if ep in ledger_ours else "probe-log"
        ours = (ledger_ours.get(ep) if ep in ledger_ours else log_ours.get(ep, 0)) + int(rec.get("calls", 0) or 0)
        slots = safe_parallel_slots(rec.get("theirs", {}), ours, doe_calls_per_slot)
        status = rec.get("check", {}).get("status", "skipped")
        bucket = "ok" if status == "ok" else ("failed" if status == "failed" else "skipped")
        counts[bucket] += 1
        if bucket == "ok":
            total += slots["safe_parallel_slots"]
        else:
            slots = {**slots, "safe_parallel_slots": 0, "basis": f"check_{status}"}
        cache = rec.get("actions_cache") or {}
        if rec.get("catalog", {}).get("cache") == "hit":
            cache_stats["catalog_hit"] += 1
        elif rec.get("catalog", {}).get("cache") == "miss":
            cache_stats["catalog_miss"] += 1
        if cache:
            cache_stats["jobs"].append({"endpoint": ep, **cache})
            if cache.get("pip_cache_hit") is not None:
                cache_stats["pip_hit"] = cache.get("pip_cache_hit")
        out_rows.append({**rec, "ours": {"calls_24h": ours, "source": source}, "slots": slots})
    durations = [j.get("job_duration_s") for j in cache_stats["jobs"] if isinstance(j.get("job_duration_s"), (int, float))]
    cache_stats["job_duration_s_max"] = max(durations) if durations else None
    cache_stats["job_duration_s_sum"] = sum(durations) if durations else None
    top = sorted((r for r in out_rows if r["slots"]["safe_parallel_slots"] > 0),
                 key=lambda r: -r["slots"]["safe_parallel_slots"])[:5]
    return {
        "schema": SCHEMA, "generated_at": now_iso(), "safety_factor": SAFETY,
        "doe_calls_per_slot_day": doe_calls_per_slot,
        "max_completion_calls_per_endpoint": MAX_COMPLETIONS_PER_ENDPOINT,
        "total_safe_parallel_slots": total, "counts": counts,
        "top_endpoints": [{"endpoint": r["endpoint"], "slots": r["slots"]["safe_parallel_slots"]} for r in top],
        "missing_secrets": sorted(r["secret_env"] for r in out_rows
                                  if not r.get("secret_present") and r.get("secret_env")),
        "actions_cache": cache_stats, "run": run_meta or {}, "endpoints": out_rows,
    }


def log_line(rec: dict[str, Any]) -> str:
    return json.dumps({"observed_at": rec.get("observed_at"), "endpoint": rec.get("endpoint"),
                       "check": rec.get("check", {}).get("status"), "model": rec.get("check", {}).get("model"),
                       "calls": rec.get("calls", 0), "slots": rec.get("slots", {}).get("safe_parallel_slots")},
                      sort_keys=True)


# --------------------------------------------------------------------------- cli
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("matrix")
    p = sub.add_parser("probe")
    p.add_argument("--endpoint", required=True)
    p.add_argument("--token-env", default="", help="env var holding the token (matrix mode)")
    p.add_argument("--cache-dir", default="")
    p.add_argument("--output", required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--records", required=True, help="glob of raw record JSON files")
    a.add_argument("--ledger", default="")
    a.add_argument("--log", default="ops/inference/endpoint-probe-log.jsonl")
    a.add_argument("--output", default="ops/inference/endpoint-availability.json")
    a.add_argument("--doe-calls-per-slot", type=int, default=DEFAULT_DOE_CALLS_PER_SLOT_DAY)
    args = ap.parse_args(argv)

    if args.mode == "matrix":
        print(json.dumps({"include": build_matrix()}, separators=(",", ":")))
        return 0
    if args.mode == "probe":
        token = os.environ.get(args.token_env) if args.token_env else None
        if not token:
            token, _ = pmc.resolve_secret(args.endpoint)
        rec = probe_endpoint(args.endpoint, token or None, cache_dir=args.cache_dir or None)
        cache = {}
        for key, env in (("catalog_cache_hit", "CATALOG_CACHE_HIT"), ("pip_cache_hit", "PIP_CACHE_HIT")):
            if os.environ.get(env) is not None:
                cache[key] = os.environ.get(env) == "true"
        if os.environ.get("JOB_STARTED_EPOCH", "").isdigit():
            cache["job_duration_s"] = int(time.time()) - int(os.environ["JOB_STARTED_EPOCH"])
        if cache:
            rec["actions_cache"] = cache
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        print(f"ENDPOINT {args.endpoint} secret_present={rec['secret_present']} catalog={rec['catalog']['status']} check={rec['check']['status']}")
        return 0
    records = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(args.records))]
    ledger = None
    if args.ledger and Path(args.ledger).exists():
        try:
            ledger = json.loads(Path(args.ledger).read_text())
        except json.JSONDecodeError:
            ledger = None
    log_path = Path(args.log)
    lines = log_path.read_text().splitlines() if log_path.exists() else []
    meta = {k.lower(): os.environ[k] for k in ("GITHUB_RUN_ID", "GITHUB_SHA") if os.environ.get(k)}
    doc = aggregate(records, ledger, lines, args.doe_calls_per_slot, meta)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    with log_path.open("a", encoding="utf-8") as fh:
        for rec in doc["endpoints"]:
            fh.write(log_line(rec) + "\n")
    print(f"total_safe_parallel_slots={doc['total_safe_parallel_slots']} counts={json.dumps(doc['counts'])} "
          f"top={json.dumps(doc['top_endpoints'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
