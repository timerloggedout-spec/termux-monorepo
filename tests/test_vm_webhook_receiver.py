"""Offline tests for the VM bounded webhook intake leg.
Run: python3 -m pytest tests/test_vm_webhook_receiver.py
"""
import hashlib, hmac, importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "vm_webhook_receiver",
    Path(__file__).resolve().parents[1] / "ops" / "receiver-mesh" / "vm" / "vm_webhook_receiver.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def _sig(secret, body):
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

def test_signature_roundtrip():
    body = b'{"event":"ping"}'
    assert mod.verify_signature("s3cret", body, _sig("s3cret", body))
    assert not mod.verify_signature("wrong", body, _sig("s3cret", body))
    assert not mod.verify_signature("s3cret", body, None)
    assert not mod.verify_signature("", body, _sig("s3cret", body))

def test_envelope_is_allowlisted_only():
    payload = {"event": "issues", "action": "opened", "repository": {"full_name": "o/r"},
               "sender": {"login": "octo"}, "raw_secret_blob": "never-forward", "token": "x"}
    env = mod.normalize("github", payload, "d1")
    assert set(env) == set(mod.ENVELOPE_FIELDS)
    assert env["route_status"] == "unrouted_flagged" and env["delivery_target"] is None
    assert env["repo"] == "o/r" and env["actor"] == "octo"
    assert "never-forward" not in json.dumps(env)

def test_intake_log_durable_and_dedupes(tmp_path):
    log = mod.IntakeLog(tmp_path / "intake.jsonl")
    env = mod.normalize("test", {"event": "ping"}, "d9")
    assert log.append(env) is True
    assert log.append(env) is False  # duplicate delivery_id
    # durability: a fresh instance over the same file still dedupes
    log2 = mod.IntakeLog(tmp_path / "intake.jsonl")
    assert log2.count() == 1
    assert log2.append(env) is False

ROUTES = {"github": {"chat_id": "chat-1", "role": "connectors"},
          "meta": {"chat_id": "chat-2", "role": "social-connectors"}}

def test_route_resolution_known_and_unknown():
    env = mod.normalize("github", {"event": "push"}, "d2", ROUTES)
    assert env["route_status"] == "routed"
    assert env["delivery_target"] == {"chat_id": "chat-1", "role": "connectors"}
    env2 = mod.normalize("meta", {"event": "messages"}, "d3", ROUTES)
    assert env2["delivery_target"]["chat_id"] == "chat-2"
    # unknown source: still normalized (logged), flagged, never dropped
    env3 = mod.normalize("zzz-unknown", {"event": "ping"}, "d4", ROUTES)
    assert env3["route_status"] == "unrouted_flagged" and env3["delivery_target"] is None

def test_routes_json_carried_by_profile():
    routes_file = Path(__file__).resolve().parents[1] / "ops" / "receiver-mesh" / "vm" / "routes.json"
    doc = json.loads(routes_file.read_text())
    assert doc["schema"] == "vm-webhook-routes/v1"
    for source, target in doc["routes"].items():
        assert target["chat_id"] and target["role"], source
