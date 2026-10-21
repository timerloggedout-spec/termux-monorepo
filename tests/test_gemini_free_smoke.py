import json
from datetime import timedelta
from unittest.mock import patch
import urllib.error

import pytest

from scripts.ops import gemini_free_smoke as smoke

KEY = "synthetic-api-key-not-a-real-credential"
OAUTH = "synthetic-oauth-not-a-real-credential"
RESOURCE = "projects/123456789/locations/global/keys/synthetic-key-id"
NOW = smoke.PRICE_VERIFIED_AT + timedelta(minutes=1)


def project_replies():
    return [{"keyString": KEY},
            {"name": "projects/123456789", "projectId": "synthetic-project", "state": "ACTIVE"},
            {"projectId": "synthetic-project", "billingEnabled": False, "billingAccountName": ""}]


def model_reply():
    return {"name": "models/" + smoke.MODEL, "supportedGenerationMethods": ["generateContent"]}


def completion():
    return {"modelVersion": smoke.MODEL, "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "OK"}]}}]}


def run(replies=None, **kwargs):
    replies = replies if replies is not None else project_replies() + [model_reply()] + project_replies() + [completion()]
    with patch.object(smoke, "request", side_effect=replies) as request:
        report = smoke.observe(KEY, oauth=OAUTH, resource=RESOURCE, execute=True, now=NOW, **kwargs)
    return report, request


def test_default_never_contacts_any_provider():
    with patch.object(smoke, "request") as request:
        report = smoke.observe(KEY)
    request.assert_not_called()
    assert report["reason"] == "explicit_smoke_not_requested"


@pytest.mark.parametrize("key", [None, "", "secret\nvalue", "non-ascii-\u00e9", True])
def test_missing_or_invalid_secret_never_contacts_provider(key):
    with patch.object(smoke, "request") as request:
        report = smoke.observe(key, execute=True, now=NOW)
    request.assert_not_called()
    assert not report["inference_attempted"]


@pytest.mark.parametrize("resource", [None, "", "projects/123/locations/us/keys/key", "projects/123/locations/global/keys/../other", "https://evil.invalid", "projects/0123/locations/global/keys/key"])
def test_key_resource_must_be_exact_global_project_resource(resource):
    with patch.object(smoke, "request") as request:
        report = smoke.observe(KEY, resource=resource, oauth=OAUTH, execute=True, now=NOW)
    request.assert_not_called()
    assert report["reason"] == "project_api_key_resource_missing_or_invalid"


def test_api_key_only_is_not_project_tier_proof():
    with patch.object(smoke, "request") as request:
        report = smoke.observe(KEY, resource=RESOURCE, execute=True, now=NOW)
    request.assert_not_called()
    assert report["reason"] == "project_project_read_authorization_missing"


@pytest.mark.parametrize("now", [smoke.PRICE_VERIFIED_AT - timedelta(seconds=1), smoke.PRICE_VERIFIED_AT + timedelta(days=2), smoke.PRICE_VERIFIED_AT.replace(tzinfo=None)])
def test_stale_price_blocks_before_key_access(now):
    with patch.object(smoke, "request") as request:
        report = smoke.observe(KEY, resource=RESOURCE, oauth=OAUTH, execute=True, now=now)
    request.assert_not_called()
    assert report["reason"] == "official_zero_price_evidence_expired"


@pytest.mark.parametrize("binding", [{}, {"keyString": "another-key"}, {"keyString": False}])
def test_wrong_project_key_never_reaches_billing_or_inference(binding):
    report, request = run([binding])
    assert request.call_count == 1
    assert report["reason"] == "project_api_key_project_binding_unverified"


@pytest.mark.parametrize("project", [{}, {"name": "projects/987654321", "projectId": "synthetic-project", "state": "ACTIVE"}, {"name": "projects/123456789", "projectId": "synthetic-project", "state": "DELETE_REQUESTED"}, {"name": "projects/123456789", "projectId": "../evil", "state": "ACTIVE"}])
def test_active_exact_project_required(project):
    report, request = run([{"keyString": KEY}, project])
    assert request.call_count == 2
    assert report["reason"] == "project_active_project_unverified"


@pytest.mark.parametrize("billing", [
    {}, {"projectId": "synthetic-project", "billingEnabled": False},
    {"projectId": "synthetic-project", "billingEnabled": True, "billingAccountName": ""},
    {"projectId": "synthetic-project", "billingEnabled": 0, "billingAccountName": ""},
    {"projectId": "synthetic-project", "billingEnabled": False, "billingAccountName": "billingAccounts/paid"},
    {"projectId": "another-project", "billingEnabled": False, "billingAccountName": ""},
])
def test_inactive_paid_or_unknown_billing_is_not_free(billing):
    report, request = run(project_replies()[:2] + [billing])
    assert request.call_count == 3
    assert report["reason"] == "project_unbilled_project_unverified"
    assert not report["inference_attempted"]


@pytest.mark.parametrize("model", [{}, {"name": "models/another", "supportedGenerationMethods": ["generateContent"]}, {"name": "models/" + smoke.MODEL, "supportedGenerationMethods": []}])
def test_exact_model_generation_capability_required(model):
    report, request = run(project_replies() + [model])
    assert request.call_count == 4
    assert not report["inference_attempted"]


def test_billing_recheck_blocks_if_account_changes():
    report, request = run(project_replies() + [model_reply()] + project_replies()[:2] + [{"projectId": "synthetic-project", "billingEnabled": True, "billingAccountName": "billingAccounts/paid"}])
    assert request.call_count == 7
    assert not report["inference_attempted"]


def test_one_fixed_public_prompt_no_fallback_and_no_credential_leak():
    report, request = run()
    assert report["inference_ok"]
    assert report["completion_requests"] == 1
    assert request.call_count == 8
    url, key, payload = request.call_args.args
    assert url == smoke.CHAT_URL and key == KEY
    assert payload == {"contents": [{"role": "user", "parts": [{"text": "Reply with exactly: OK"}]}], "generationConfig": {"maxOutputTokens": 16, "temperature": 0}}
    serialized = json.dumps(report)
    assert all(secret not in serialized for secret in [KEY, OAUTH, RESOURCE, "synthetic-project", "123456789"])
    assert not report["production_admission_changed"]
    assert not report["paid_fallback_allowed"]


@pytest.mark.parametrize("reply", [{}, {"modelVersion": "another-model", "candidates": completion()["candidates"]}, {"modelVersion": smoke.MODEL, "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "PRIVATE UPSTREAM TEXT"}]}}]}])
def test_invalid_completion_is_not_success_and_body_is_discarded(reply):
    report, request = run(project_replies() + [model_reply()] + project_replies() + [reply])
    assert request.call_count == 8
    assert not report["inference_ok"]
    assert "PRIVATE" not in json.dumps(report)


def test_rate_limit_has_no_retry_or_fallback():
    report, request = run(project_replies() + [model_reply()] + project_replies() + [smoke.SmokeError("http_429")])
    assert request.call_count == 8
    assert report["reason"] == "inference_http_429"
    assert report["completion_requests"] == 1


@pytest.mark.parametrize("url,payload", [("https://evil.invalid", None), (smoke.MODEL_URL + "?key=secret", None), (smoke.MODEL_URL, {}), (smoke.CHAT_URL, None)])
def test_transport_refuses_unreviewed_urls_and_methods(url, payload):
    with patch.object(smoke.urllib.request, "build_opener") as opener:
        with pytest.raises(smoke.SmokeError, match="invalid_request"):
            smoke.request(url, KEY, payload)
    opener.assert_not_called()


def test_transport_header_isolation_bounds_and_no_redirect():
    assert smoke.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.invalid") is None
    for url, credential, header in [(smoke.MODEL_URL, KEY, "X-goog-api-key"), ("https://apikeys.googleapis.com/v2/" + RESOURCE + "/keyString", OAUTH, "Authorization")]:
        response = type("Response", (), {"status": 200, "read": lambda self, n: b"{}", "__enter__": lambda self: self, "__exit__": lambda *args: None})()
        with patch.object(smoke.urllib.request, "build_opener") as build:
            build.return_value.open.return_value = response
            smoke.request(url, credential)
        req = build.return_value.open.call_args.args[0]
        assert req.get_header(header) == (credential if header != "Authorization" else "Bearer " + credential)
        assert credential not in req.full_url
        assert build.return_value.open.call_args.kwargs["timeout"] == smoke.TIMEOUT


def test_transport_http_error_discards_body_url_and_secret():
    error = urllib.error.HTTPError("https://private?secret=value", 403, "PRIVATE", {}, None)
    with patch.object(smoke.urllib.request, "build_opener") as build:
        build.return_value.open.side_effect = error
        with pytest.raises(smoke.SmokeError) as captured:
            smoke.request(smoke.MODEL_URL, KEY)
    assert str(captured.value) == "http_403"


def test_cli_without_execute_has_no_network(tmp_path):
    path = tmp_path / "receipt.json"
    with patch.object(smoke, "request") as request:
        assert smoke.main(["--output", str(path)]) == 0
    request.assert_not_called()
    assert json.loads(path.read_text())["completion_requests"] == 0


@pytest.mark.parametrize("text", [None, False, 42, {}, []])
def test_malformed_completion_text_is_a_sanitized_failure(text):
    reply = completion()
    reply["candidates"][0]["content"]["parts"][0]["text"] = text
    report, _ = run(project_replies() + [model_reply()] + project_replies() + [reply])
    assert report["reason"] == "unexpected_completion"
    assert not report["inference_ok"]


@pytest.mark.parametrize("raw,reason", [(b"x" * (smoke.MAX_BYTES + 1), "response_too_large"), (b"not json", "invalid_response"), (b"[]", "invalid_response"), (b"\xff", "invalid_response")])
def test_transport_response_bounds_and_json_shape(raw, reason):
    response = type("Response", (), {"status": 200, "read": lambda self, n: raw, "__enter__": lambda self: self, "__exit__": lambda *args: None})()
    with patch.object(smoke.urllib.request, "build_opener") as build:
        build.return_value.open.return_value = response
        with pytest.raises(smoke.SmokeError, match=reason):
            smoke.request(smoke.MODEL_URL, KEY)


def test_no_secret_or_auth_response_written_by_cli(tmp_path, capsys):
    path = tmp_path / "receipt.json"
    with patch.dict(smoke.os.environ, {"GEMINI_API_KEY": KEY, "GOOGLE_OAUTH_ACCESS_TOKEN": OAUTH, "GEMINI_API_KEY_RESOURCE": RESOURCE}):
        with patch.object(smoke, "observe", return_value={"inference_ok": False, "completion_requests": 0, "reason": "project_read_authorization_missing"}):
            assert smoke.main(["--execute", "--output", str(path)]) == 1
    output = path.read_text() + capsys.readouterr().out
    assert all(secret not in output for secret in [KEY, OAUTH, RESOURCE])


@pytest.mark.parametrize("error", [smoke.http.client.IncompleteRead(b"PRIVATE"), smoke.http.client.BadStatusLine("PRIVATE")])
def test_transport_protocol_errors_are_sanitized(error):
    with patch.object(smoke.urllib.request, "build_opener") as build:
        build.return_value.open.side_effect = error
        with pytest.raises(smoke.SmokeError) as captured:
            smoke.request(smoke.MODEL_URL, KEY)
    assert str(captured.value) == "transport_unavailable"


def test_decoder_recursion_is_sanitized():
    response = type("Response", (), {"status": 200, "read": lambda self, n: b"{}", "__enter__": lambda self: self, "__exit__": lambda *args: None})()
    with patch.object(smoke.urllib.request, "build_opener") as build:
        build.return_value.open.return_value = response
        with patch.object(smoke.json, "loads", side_effect=RecursionError("PRIVATE")):
            with pytest.raises(smoke.SmokeError) as captured:
                smoke.request(smoke.MODEL_URL, KEY)
    assert str(captured.value) == "invalid_response"
