"""Tests for the System One adapter + observatory decide stage.

The wire shape is the TypeSafe-compatible decision API implemented by
Kev (POST /v1/systemone) and simple-jev (POST /v1/classifier, alias):
{state, model, questions{type: choice|score|noul}} -> {answers{...}}.
All transports are stubbed; no network, no credential.
"""
import asyncio
import json

import pytest

from deepcli.llm.adapters.systemone import Adapter, Decision
from deepcli.observatory.decide import decide_check, rubric_questions
from deepcli.observatory import dispatch


CANNED = {
    "model": "kev-latest",
    "answers": {
        "quality": {"type": "score", "score": 0.8, "confidence": 0.5,
                    "probabilities": {"0": 0.2, "1": 0.8}},
        "grounding": {"type": "score", "score": 0.6, "confidence": 0.4,
                      "probabilities": {"0": 0.4, "1": 0.6}},
        "supported": {"type": "noul", "noul": 0.9},
    },
    "usage": {"input_tokens": 42, "output_tokens": 12},
    "latency_ms": 33,
}


def stub_transport(url, headers, payload):
    stub_transport.seen = (url, headers, payload)
    return CANNED


def test_decide_posts_systemone_shape():
    a = Adapter(transport=stub_transport, base_url="http://x:9000")
    dec = asyncio.run(a.decide("some state", rubric_questions(
        {"quality": "0..1 quality"})))
    url, headers, payload = stub_transport.seen
    assert url == "http://x:9000/v1/systemone"
    assert payload["state"] == "some state"
    assert payload["model"] == "kev-latest"
    q = payload["questions"]["quality"]
    assert q["type"] == "score" and q["criteria"] == ["0", "1"]
    assert isinstance(dec, Decision)
    assert dec.answers["quality"]["score"] == 0.8
    assert dec.tokens_in == 42 and dec.tokens_out == 12
    assert dec.latency_ms == 33


def test_ask_refuses_chat_contract():
    a = Adapter(transport=stub_transport)
    with pytest.raises(NotImplementedError):
        asyncio.run(a.ask("hello"))


def test_decide_check_extracts_scores():
    out = asyncio.run(decide_check(
        "artifact text", {"quality": "q", "grounding": "g"},
        base_url="http://x:9000", transport=stub_transport))
    assert out["ok"] is True
    assert out["scores"] == {"quality": 0.8, "grounding": 0.6}
    assert out["supported"] == 0.9
    assert out["role"] == "systemone"


def test_decide_check_records_failure_in_band():
    def boom(url, headers, payload):
        raise RuntimeError("connection refused")

    out = asyncio.run(decide_check("s", {"quality": "q"},
                                   base_url="http://x:1",
                                   transport=boom))
    assert out["ok"] is False
    assert "connection refused" in out["error"]


def test_rubric_questions_shape():
    qs = rubric_questions({"quality": "0..1 quality"})
    assert qs["quality"]["type"] == "score"
    assert qs["supported"]["type"] == "noul"


def test_dispatch_decide_only(monkeypatch, tmp_path):
    async def fake_decide(state, rubric=None, base_url="", model="",
                          transport=None):
        return {"role": "systemone", "ok": True,
                "scores": {"quality": 0.5}, "supported": 0.7}

    monkeypatch.setattr(dispatch, "decide_check", fake_decide)
    out = tmp_path / "rec.json"
    rc = dispatch.main(["--prompt", "state text", "--decide-only",
                        "--decide-url", "http://x:9000",
                        "--out", str(out)])
    assert rc == 0
    record = json.loads(out.read_text())
    assert record["decide"]["scores"] == {"quality": 0.5}
    assert record["artifacts"] == []


def test_dispatch_decide_only_failure(monkeypatch, tmp_path):
    async def fake_decide(state, rubric=None, base_url="", model="",
                          transport=None):
        return {"role": "systemone", "ok": False,
                "error": "RuntimeError: down"}

    monkeypatch.setattr(dispatch, "decide_check", fake_decide)
    rc = dispatch.main(["--prompt", "s", "--decide-only",
                        "--out", str(tmp_path / "r.json")])
    assert rc == 1
