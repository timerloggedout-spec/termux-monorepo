import importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "hindsight_verify", ROOT / "scripts/telemetry_ingest/hindsight_verify.py")
hv = importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)


class Resp:
    def __init__(self, body, status=200):
        self._b = body; self.status = status
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): return self._b.encode()


def test_verify_collects_stats_and_recall():
    def opener(req, timeout=None):
        if req.full_url.endswith("/health"):
            return Resp('{"status":"ok"}')
        if "llm-requests" in req.full_url:
            return Resp('{"total_requests": 7}')
        if req.full_url.endswith("/stats"):
            return Resp('{"total_memories": 42}')
        if req.full_url.endswith("/memories/recall"):
            return Resp('{"results": [{"id": 1}, {"id": 2}]}')
        raise AssertionError(req.full_url)
    out = hv.verify("https://hs.example", "bank::p", "k", opener=opener)
    assert out["memories_total"] == 42 and out["recall_hits"] == 2
    assert out["llm_stats"]["json"]["total_requests"] == 7
