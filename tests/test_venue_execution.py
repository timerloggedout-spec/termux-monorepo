"""Venue-execution machinery tests (QUE #5254).

Done-evidence pins: SUBMIT-ONCE idempotency (second fire reads
state, adapter never re-invoked) and the no-login verify (the
verification request carries no credential headers).

Run: python3 -m pytest tests/test_venue_execution.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "venues"))
import venue_execution as ve  # noqa: E402
import webform_adapter  # noqa: E402

NOW = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).parent.parent


class FakeResponse:
    def __init__(self, body=b"", status=200):
        self._body = body
        self.status = status

    def read(self, n=-1):
        return self._body[:n] if n and n > 0 else self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _write_entry(root: Path, census_reqs, bindings):
    entry = root / "entries" / "proof"
    entry.mkdir(parents=True)
    (entry / "submission-requirements.json").write_text(json.dumps(
        {"schema": "opportunity-submission-requirements/v1",
         "entry": "PROOF", "slug": "proof", "requirements": census_reqs}))
    (entry / "venue-execution.json").write_text(json.dumps(
        {"schema": "venue-execution-bindings/v1", "bindings": bindings}))
    (root / "media.bin").write_bytes(b"proof-bytes")
    return root


def _census_req(**kw):
    base = {"id": "up", "class": "fleet-executable", "discharged": False,
            "submit_once": True, "requirement": "upload the thing"}
    base.update(kw)
    return base


def test_class_gating(tmp_path):
    root = _write_entry(tmp_path, [_census_req(**{"class": "owner-hand"})],
                        {"up": {"adapter": "webform", "endpoint": "https://x"}})
    plan = ve.plan_execution(ve.load_json(
        root / "entries" / "proof" / "submission-requirements.json"),
        ve.load_json(root / "entries" / "proof" / "venue-execution.json"),
        "up")
    assert plan["action"] == "skip"
    assert "owner-hand" in plan["reason"]


def test_submit_once_second_fire_reads_state_never_resends(tmp_path):
    root = _write_entry(tmp_path, [_census_req()],
                        {"up": {"adapter": "webform", "venue": "test",
                                "endpoint": "https://venue.test/post",
                                "file_field": "file"}})
    calls = {"post": 0}

    def transport(req, timeout=None):
        calls["post"] += 1
        return FakeResponse(b"https://venue.test/public/abc.txt")

    def opener(req, timeout=None):
        return FakeResponse(b"proof-bytes")

    import unittest.mock as mock
    state = root / "state.json"
    with mock.patch.object(ve, "verify_public",
                           lambda url, expect=None: {"ok": True,
                                                     "status": 200,
                                                     "bytes": 11}):
        first = ve.execute("proof", "up", str(root / "media.bin"), root,
                           state, now=NOW, run_id="r1", transport=transport)
        assert first["outcome"] == "executed"
        assert calls["post"] == 1
        second = ve.execute("proof", "up", str(root / "media.bin"), root,
                            state, now=NOW, run_id="r2", transport=transport)
        assert second["outcome"] == "already_executed"
        assert second["public_url"] == "https://venue.test/public/abc.txt"
        assert calls["post"] == 1  # the adapter was NOT invoked again


def test_verify_is_unauthenticated():
    seen = {}

    def opener(req, timeout=None):
        seen["headers"] = dict(req.header_items())
        return FakeResponse(b"hello public world")

    result = ve.verify_public("https://venue.test/public/abc.txt",
                                expect_contains="public", opener=opener)
    assert result["ok"] is True and result["status"] == 200
    assert "Authorization" not in seen["headers"]
    assert "Cookie" not in seen["headers"]


def test_webform_multipart_and_url_extraction():
    body, boundary = webform_adapter.build_multipart(
        {"reqtype": "fileupload"}, "file", None)
    assert b"reqtype" in body and b"fileupload" in body
    assert webform_adapter.extract_url("https://0x0.st/abc.txt\n", None) \
        == "https://0x0.st/abc.txt"
    assert webform_adapter.extract_url(
        "see https://x.test/f", r"(https://\S+)") == "https://x.test/f"
    assert webform_adapter.extract_url("no url here", None) is None


def test_webform_sends_descriptive_user_agent():
    seen = {}

    def transport(req, timeout=None):
        seen["ua"] = req.headers.get("User-agent")
        return FakeResponse(b"https://venue.test/public/x.txt")

    result = webform_adapter.execute(
        {"endpoint": "https://venue.test/post", "file_field": None},
        artifact=None, transport=transport)
    assert result["status"] == "executed"
    assert "venue-execution" in seen["ua"]


def test_clips_adapter_named_refusal_without_credential(monkeypatch):
    monkeypatch.delenv("CLIPS_FLEET_TOKEN", raising=False)
    import clips_adapter
    result = clips_adapter.execute(
        {"credential_env": "CLIPS_FLEET_TOKEN"}, artifact="/tmp/x.mp4")
    assert result["status"] == "refused"
    assert result["reason"] == "venue_auth_missing"


def test_clips_read_leg_uses_public_context(monkeypatch):
    import clips_adapter

    def opener(req, timeout=None):
        assert "agent-context.json?id=clip9" in req.full_url
        return FakeResponse(json.dumps(
            {"clip": {"publicPageUrl": "https://clips.agent-native.com/share/clip9"}}).encode())

    result = clips_adapter.execute({"clip_id": "clip9"}, artifact=None,
                                   transport=opener)
    assert result["status"] == "executed"
    assert result["public_url"].endswith("/share/clip9")


def test_proof_entry_fixture_is_wellformed():
    census = ve.load_json(ROOT / "entries" / "venue-machinery-proof"
                          / "submission-requirements.json")
    bindings = ve.load_json(ROOT / "entries" / "venue-machinery-proof"
                            / "venue-execution.json")
    plan = ve.plan_execution(census, bindings, "proof-upload")
    assert plan["action"] == "execute"
    assert plan["binding"]["adapter"] == "webform"
