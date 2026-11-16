import importlib.util, json, urllib.error, io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "retain_payloads", ROOT / "scripts/telemetry_ingest/retain_payloads.py")
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

PAYLOADS = [
    {"content": "unit a", "metadata": {"source_id": "s1", "unit_id": "u1", "evidence_hash": "h1"}},
    {"content": "unit b", "metadata": {"kind": "density_actor", "actor": "Grok", "evidence_hash": "h2"}},
]


class Resp:
    status = 202
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_endpoint_and_body_shape():
    seen = {}

    def opener(req, timeout=None):
        seen["url"] = req.full_url
        seen["auth"] = req.headers.get("Authorization")
        seen["body"] = json.loads(req.data)
        return Resp()

    s = rp.retain(PAYLOADS, "https://hs.example/", "bank::primary", "k3y", opener=opener)
    assert s["ok"] == 2 and s["failed"] == 0 and s["batches"] == 1
    assert seen["url"] == "https://hs.example/v1/default/banks/bank%3A%3Aprimary/memories"
    assert seen["auth"] == "Bearer k3y"
    items = seen["body"]["items"]
    assert seen["body"]["async"] is True
    assert items[0]["document_id"] == "telemetry:s1:u1"
    assert items[1]["document_id"] == "density:density_actor:Grok"
    assert "actor:Grok" in items[1]["tags"]


def test_http_error_recorded_as_gate_evidence():
    def opener(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 404, "not found", {}, io.BytesIO(b'{"detail":"no route"}'))

    s = rp.retain(PAYLOADS, "https://hs.example", "b", "k", opener=opener)
    assert s["ok"] == 0 and s["failed"] == 2
    assert s["first_error"]["status"] == 404
    assert "no route" in s["first_error"]["body_excerpt"]

def test_state_skip_and_max_items():
    calls = []
    def opener(req, timeout=None):
        calls.append(json.loads(req.data)); return Resp()
    state = {"telemetry:s1:u1": "h1"}
    s = rp.retain(PAYLOADS, "https://hs.example", "b", "k", opener=opener, state=dict(state))
    assert s["skipped_unchanged"] == 1 and s["ok"] == 1
    assert len(calls) == 1 and calls[0]["items"][0]["document_id"] == "density:density_actor:Grok"
    s2 = rp.retain(PAYLOADS, "https://hs.example", "b", "k", opener=opener, max_items=1)
    assert s2["ok"] == 1 and s2["attempted"] == 1
