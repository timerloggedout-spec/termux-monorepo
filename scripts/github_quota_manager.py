"""Read-only GitHub REST quota observer. Counters are private observation data; CLI output is status-only.

Documented policy context: REST user 5,000/hour; Actions GITHUB_TOKEN 1,000/repository/hour
(15,000 for enterprise resources); installation token base 5,000/hour with documented scaling
up to 12,500, or 15,000 for Enterprise Cloud. GraphQL is a distinct points budget. These
values are documentation, not token-class inference or universal enforcement guarantees.
Actions billing minutes/storage, workflow concurrency, and API quota are distinct products.
"""
from __future__ import annotations
import argparse, copy, datetime as dt, hashlib, http.client, json, math, os, sys, time, urllib.error, urllib.parse, urllib.request
from threading import Event, Lock

API_URL = "https://api.github.com/rate_limit"
API_HOST = "api.github.com"
API_PATH = "/rate_limit"
TOKEN_CLASSES = frozenset(("github_token", "user_token", "app_installation", "unknown"))
RESOURCES = frozenset(("core", "search", "code_search", "graphql", "integration_manifest", "dependency_snapshots", "dependency_sbom", "actions_runner_registration", "source_import", "scim", "code_scanning_upload", "code_scanning_autofix", "copilot_usage_records", "audit_log", "audit_log_streaming", "enterprise_token_inventory"))
MAX_BODY, MAX_TTL, REQUEST_TIMEOUT = 65536, 30.0, 8
OFFICIAL_SOURCES = {
    "resource_buckets": "https://docs.github.com/en/rest/rate-limit/rate-limit#get-rate-limit-status-for-the-authenticated-user",
    "rest": "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api",
    "graphql": "https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api",
    "actions": "https://docs.github.com/en/actions/reference/limits",
}
# Static documented references; do not use these to infer class or claim API enforcement.
DOCUMENTED_REST_LIMITS = {"user": 5000, "github_token_per_repository": 1000, "enterprise_resource_per_repository": 15000, "app_installation_base": 5000, "app_installation_scaled_max": 12500, "app_installation_enterprise": 15000}
DOCUMENTED_GRAPHQL_LIMITS = {"user_points_per_hour": 5000, "github_token_points_per_repository_hour": 1000, "app_installation_base_points_per_hour": 5000, "app_installation_scaled_max_points_per_hour": 12500, "app_installation_enterprise_points_per_hour": 10000}
_lock = Lock()
_cache: dict[str, tuple[float, dict]] = {}
_inflight: dict[str, Event] = {}
_cooldowns: dict[str, float] = {}
class QuotaError(ValueError): pass

def reserve_allows(read_cost: int, remaining_budget: int | None, reserve: int) -> bool:
    """Local caller-side budget guard only; it cannot enforce GitHub's global limits."""
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in (read_cost, reserve)):
        raise QuotaError("invalid_local_reserve_policy")
    return remaining_budget is not None and isinstance(remaining_budget, int) and not isinstance(remaining_budget, bool) and remaining_budget >= read_cost + reserve

def normalize(payload, *, now=None, token_class="unknown"):
    """Validate private numeric counters while treating API-reported zero buckets as unknown."""
    if token_class not in TOKEN_CLASSES: raise QuotaError("invalid_token_class")
    now = time.time() if now is None else now
    if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
        raise QuotaError("invalid_observation_time")
    if not isinstance(payload, dict) or not isinstance(payload.get("resources"), dict): raise QuotaError("malformed_response")
    resources = payload["resources"]
    if "core" not in resources or "search" not in resources: raise QuotaError("required_resource_missing")
    out = {}
    for name, item in resources.items():
        if name not in RESOURCES: continue
        if not isinstance(item, dict): raise QuotaError("malformed_resource")
        values = {}
        for field in ("limit", "remaining", "used", "reset"):
            value = item.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0: raise QuotaError("malformed_counter")
            values[field] = value
        if values["limit"] == 0:
            out[name] = None
            continue
        if values["remaining"] > values["limit"] or values["used"] > values["limit"]: raise QuotaError("inconsistent_counters")
        if values["reset"] <= now or values["reset"] > now + 31 * 86400: raise QuotaError("stale_or_future_reset")
        values["dimension"] = "points" if name == "graphql" else "requests"
        values["scope"] = "credential_selected_resource_bucket"
        values["reset_semantics"] = "source_supplied_epoch_seconds"
        out[name] = values
    out.setdefault("graphql", None)
    return {"status":"observed", "source":"github_rest_rate_limit", "token_class":token_class,
            "observed_at":dt.datetime.fromtimestamp(now, dt.timezone.utc).isoformat(), "resources":out,
            "entitlement":"unknown; token class and resource counters do not establish account plan",
            "secondary_limits":"unknown; honor observed throttling, never infer remaining secondary capacity",
            "actions_product_quotas":"unknown"}

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None
_DEFAULT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect()).open

def _request(token, opener=_DEFAULT_OPENER, *, now=None, token_class="unknown", sleeper=time.sleep):
    req = urllib.request.Request(API_URL, headers={"Accept":"application/vnd.github+json", "X-GitHub-Api-Version":"2022-11-28", **({"Authorization":"Bearer " + token} if token else {})}, method="GET")
    try:
        response = opener(req, timeout=REQUEST_TIMEOUT)
        with response:
            final = getattr(response, "geturl", lambda: API_URL)()
            parsed = urllib.parse.urlparse(final)
            if parsed.scheme != "https" or parsed.hostname != API_HOST or parsed.path != API_PATH or parsed.query or parsed.fragment:
                raise QuotaError("unverified_response_target")
            status = getattr(response, "status", 200)
            if status in (403, 429):
                headers = getattr(response, "headers", {})
                delay = _backoff(headers, sleeper)
                error = QuotaError("secondary_or_http_limited"); error.retry_after = delay
                raise error
            body=response.read(MAX_BODY+1)
            if status != 200 or len(body)>MAX_BODY: raise QuotaError("http_or_size_error")
            return normalize(json.loads(body), now=now, token_class=token_class)
    except urllib.error.HTTPError as exc:
        if exc.code in (403,429):
            delay = _backoff(exc.headers or {}, sleeper)
            error = QuotaError("secondary_or_http_limited"); error.retry_after = delay
            raise error from None
        raise QuotaError("http_error") from None
    except QuotaError: raise
    except (OSError, TimeoutError, json.JSONDecodeError, http.client.HTTPException, ValueError): raise QuotaError("transport_or_json_error") from None

def _backoff(headers, sleeper):
    """Compute cooldown metadata without waiting; sleeper is a no-op compatibility hook."""
    value = headers.get("Retry-After") if headers else None
    try:
        delay = max(0, int(value)) if value is not None else None
    except (TypeError, ValueError):
        try:
            from email.utils import parsedate_to_datetime
            delay = max(0, math.ceil(parsedate_to_datetime(value).timestamp() - time.time()))
        except (TypeError, ValueError, AttributeError, OverflowError):
            delay = None
    if headers and headers.get("X-RateLimit-Remaining") == "0":
        try:
            reset_delay = max(0, math.ceil(int(headers.get("X-RateLimit-Reset")) - time.time()))
            delay = max(delay or 0, reset_delay)
        except (TypeError, ValueError, OverflowError):
            pass
    delay = 60 if delay is None else delay
    if delay > 3600:
        error = QuotaError("retry_after_exceeds_local_wait_bound"); error.retry_after = delay
        raise error
    return delay

def _key(token, token_class="unknown"):
    # Digest is process-memory-only; never persist or return it.
    identity = (token_class + "\0" + (token or "<anonymous>")).encode()
    return hashlib.sha256(identity).hexdigest()

def observe(token=None, *, opener=_DEFAULT_OPENER, now=None, cache_seconds=5.0, token_class="unknown", sleeper=time.sleep, remaining_budget=None, reserve=0, read_cost=1):
    """One fetch per credential concurrently; process-local success cache bounded to <=30s and reset."""
    if (isinstance(cache_seconds, bool) or not isinstance(cache_seconds, (int, float))
            or not math.isfinite(cache_seconds) or not 0 <= cache_seconds <= MAX_TTL):
        raise QuotaError("cache_bound_invalid")
    if token is not None and (not isinstance(token, str) or not token or len(token) > 4096
            or any(ord(c) <= 32 or ord(c) >= 127 for c in token)):
        raise QuotaError("invalid_credential")
    wall = time.time() if now is None else now
    if isinstance(wall, bool) or not isinstance(wall, (int, float)) or not math.isfinite(wall):
        raise QuotaError("invalid_observation_time")
    if token_class not in TOKEN_CLASSES: raise QuotaError("invalid_token_class")
    # Caller-supplied local budget estimate protects before the network read;
    # it is deliberately not inferred from credential text or sold as API-wide enforcement.
    if remaining_budget is not None and not reserve_allows(read_cost, remaining_budget, reserve):
        raise QuotaError("local_reserve_threshold")
    key=_key(token, token_class); cooldown_key=_key(token); moment=time.monotonic()
    with _lock:
        if moment < _cooldowns.get(cooldown_key, 0): raise QuotaError("rate_limit_cooldown")
        hit=_cache.get(key)
        if (hit and cache_seconds > 0 and moment-hit[0] < min(cache_seconds, max(0, hit[1].get("_ttl", 0)))
                and hit[1].get("_observed", wall + 1) <= wall < hit[1].get("_reset", 0)):
            return copy.deepcopy(hit[1]["data"])
        event=_inflight.get(key)
        if event is None:
            event=Event(); _inflight[key]=event; owner=True
        else: owner=False
    if not owner:
        if not event.wait(REQUEST_TIMEOUT+2):
            raise QuotaError("coalesced_request_timeout")
        if getattr(event, "quota_error", None):
            raise event.quota_error
        data = getattr(event, "quota_result", None)
        if data is None:
            raise QuotaError("coalesced_request_unavailable")
        return copy.deepcopy(data)
    try:
        result=_request(token, opener, now=now, token_class=token_class, sleeper=sleeper)
        resets=[v["reset"] for v in result["resources"].values() if isinstance(v,dict)]
        ttl=min(cache_seconds, max(0, min(resets)- (time.time() if now is None else now))) if resets else 0
        with _lock:
            _cache[key]=(time.monotonic(), {"data":result,"_ttl":ttl,"_reset":min(resets) if resets else 0,"_observed":wall})
            event.quota_result = result
        return copy.deepcopy(result)
    except Exception as exc:
        with _lock:
            event.quota_error = exc
            if hasattr(exc, "retry_after"): _cooldowns[cooldown_key]=time.monotonic()+exc.retry_after
        raise
    finally:
        with _lock:
            _inflight.pop(key,None)
            event.set()

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--observe",action="store_true"); parser.add_argument("--token-class",choices=sorted(TOKEN_CLASSES),default="unknown")
    args=parser.parse_args(argv)
    if not args.observe: parser.error("--observe is required")
    try: result=observe(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"), token_class=args.token_class)
    except QuotaError as exc:
        print(json.dumps({"status":"unknown","reason":str(exc)})); return 2
    # Public CLI is intentionally status-only; no counters, reset, scopes, identifiers, or raw error text.
    print(json.dumps({"status":result["status"],"source":result["source"]},sort_keys=True)); return 0
if __name__ == "__main__": sys.exit(main())
