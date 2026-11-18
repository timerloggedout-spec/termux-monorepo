import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("endpoint_probe", ROOT / "scripts/inference/endpoint_probe.py")
ep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ep)

SECRET = "sk-TESTSECRET-0123456789abcdef"


def _rows(provider, ids, free_suffix=False, price="paid"):
    return [{"provider": provider, "id": i, "context_length": 8192, "max_output_tokens": 1024,
             "pricing_classification": price, "access_classification": "catalog_pricing_only",
             "free_suffix": free_suffix and i.endswith(":free")} for i in ids]


class Recorder:
    def __init__(self, status=200, headers=None):
        self.calls = []
        self.status = status
        self.headers = headers or {}

    def __call__(self, url, headers, body):
        self.calls.append((url, headers, body))
        return self.status, self.headers


def test_matrix_covers_every_endpoint():
    matrix = ep.build_matrix()
    assert {m["endpoint"] for m in matrix} == set(ep.pmc.ENDPOINTS)
    assert all(set(m) >= {"secret", "alias1", "alias2", "alias3"} for m in matrix)


def test_route_classes():
    assert ep.route_class("groq")["completion_url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert ep.route_class("gemini")["route_class"].startswith("native:gemini")
    assert ep.route_class("cohere")["route_class"] == "catalog_only"


def test_one_call_cap_per_endpoint():
    post = Recorder()
    budget = ep.CallBudget()
    poll = lambda p, t: (_rows(p, ["a:free", "b:free"], free_suffix=True), {})
    rec1 = ep.probe_endpoint("openrouter", SECRET, budget=budget, poll=poll, post=post)
    rec2 = ep.probe_endpoint("openrouter", SECRET, budget=budget, poll=poll, post=post)
    assert rec1["check"]["status"] == "ok"
    assert rec2["check"]["status"] == "skipped:call_cap"
    assert len(post.calls) == 1
    assert post.calls[0][2]["max_tokens"] == 1


def test_free_only_gate():
    post = Recorder()
    poll = lambda p, t: (_rows(p, ["paid-model", "other"], free_suffix=True), {})
    rec = ep.probe_endpoint("openrouter", SECRET, poll=poll, post=post)
    assert rec["check"]["status"] == "skipped:no_free_model"
    assert post.calls == []
    # paid catalog on a non-free-tier provider stays gated
    rec = ep.probe_endpoint("mistral", SECRET, poll=lambda p, t: (_rows(p, ["m"], price="unknown"), {}), post=post)
    assert rec["check"]["status"] == "skipped:no_free_model"
    assert post.calls == []


def test_no_secret_skips_without_calls():
    post = Recorder()
    called = []
    rec = ep.probe_endpoint("groq", None, poll=lambda p, t: called.append(p), post=post)
    assert rec["check"]["status"] == "skipped:no_secret"
    assert rec["secret_present"] is False
    assert post.calls == [] and called == []


def test_slot_math():
    theirs = {"rpm": 30, "rpd": 14400, "remaining_minute": None, "remaining_day": None}
    # day slots = (14400-400)/50 = 280; min(30, 280)=30; *0.5 = 15
    assert ep.safe_parallel_slots(theirs, 400)["safe_parallel_slots"] == 15
    theirs = {"rpm": 20, "rpd": 50, "remaining_minute": None, "remaining_day": None}
    # day slots = (50-1)/50 = 0.98 -> floor(0.49) = 0
    assert ep.safe_parallel_slots(theirs, 1)["safe_parallel_slots"] == 0
    assert ep.safe_parallel_slots({}, 0)["basis"] == "no_declared_limits"
    theirs = ep.declared_limits("groq", {"x-ratelimit-limit-requests": "1000", "x-ratelimit-remaining-requests": "900",
                                         "x-ratelimit-limit-tokens": "6000"})
    assert theirs["rpd"] == 1000 and theirs["remaining_day"] == 900 and theirs["rpm"] == 30
    # min(30, 900/50=18) * 0.5 = 9
    assert ep.safe_parallel_slots(theirs, 5)["safe_parallel_slots"] == 9


def test_aggregate_totals_only_ok_and_no_secret_leakage(tmp_path):
    post = Recorder(headers={"x-ratelimit-limit-requests": "14400", "x-ratelimit-remaining-requests": "14000",
                             "Authorization": f"Bearer {SECRET}", "x-request-id": "r1"})
    ok = ep.probe_endpoint("groq", SECRET, poll=lambda p, t: (_rows(p, ["llama-3.1-8b-instant"]), {}), post=post)
    skipped = ep.probe_endpoint("mistral", None, poll=lambda p, t: [], post=post)
    failed = ep.probe_endpoint("cerebras", SECRET, poll=lambda p, t: (_rows(p, ["llama3.1-8b"]), {}),
                               post=lambda u, h, b: (_ for _ in ()).throw(RuntimeError(SECRET)))
    ledger = {"endpoints": [{"provider": "groq", "measured_24h": 3}]}
    doc = ep.aggregate([ok, skipped, failed], ledger, [])
    assert doc["counts"] == {"ok": 1, "skipped": 1, "failed": 1}
    groq = next(r for r in doc["endpoints"] if r["endpoint"] == "groq")
    assert groq["ours"] == {"calls_24h": 4, "source": "inference-ledger"}
    assert doc["total_safe_parallel_slots"] == groq["slots"]["safe_parallel_slots"] == 15
    assert "MISTRAL_API_KEY" in doc["missing_secrets"]
    blob = json.dumps(doc) + "".join(ep.log_line(r) for r in doc["endpoints"])
    assert SECRET not in blob
    assert "authorization" not in blob.lower()


def test_cli_probe_and_aggregate(tmp_path, monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.setenv("CATALOG_CACHE_HIT", "false")
    out = tmp_path / "rec" / "mistral.json"
    assert ep.main(["probe", "--endpoint", "mistral", "--output", str(out)]) == 0
    rec = json.loads(out.read_text())
    assert rec["check"]["status"] == "skipped:no_secret"
    assert rec["actions_cache"] == {"catalog_cache_hit": False}
    log = tmp_path / "log.jsonl"
    avail = tmp_path / "avail.json"
    for _ in range(2):
        assert ep.main(["aggregate", "--records", str(tmp_path / "rec" / "*.json"), "--log", str(log),
                        "--output", str(avail)]) == 0
    assert len(log.read_text().splitlines()) == 2  # append-only
    assert json.loads(avail.read_text())["schema"] == ep.SCHEMA


def test_catalog_cache_hit(tmp_path):
    poll_calls = []

    def poll(p, t):
        poll_calls.append(p)
        return _rows(p, ["llama-3.1-8b-instant"]), {"x-ratelimit-limit-requests": "10", "set-cookie": "x"}

    a = ep.probe_endpoint("groq", SECRET, cache_dir=str(tmp_path), poll=poll, post=Recorder())
    b = ep.probe_endpoint("groq", SECRET, cache_dir=str(tmp_path), poll=poll, post=Recorder())
    assert a["catalog"]["cache"] == "miss" and b["catalog"]["cache"] == "hit"
    assert poll_calls == ["groq"]
    assert "set-cookie" not in json.dumps(b)
