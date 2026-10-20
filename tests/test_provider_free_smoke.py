import json
from unittest.mock import patch
import urllib.error

import pytest
from scripts.ops import provider_free_smoke as smoke


def model(pricing=None):
    return {"id": smoke.MODEL, "pricing": pricing if pricing is not None else {"prompt": "0", "completion": "0", "request": "0"}}


def response():
    return {"model": smoke.MODEL, "choices": [{"message": {"content": "OK"}}], "usage": {"cost": 0}}


def run(account=None, catalog=None, completion=None):
    replies = [account if account is not None else {"data": {"is_free_tier": True}},
               {"data": [model()]} if catalog is None else catalog,
               response() if completion is None else completion]
    with patch.object(smoke, "request", side_effect=replies) as request:
        report = smoke.observe("never-serialize-secret", execute=True)
    return report, request


def test_default_never_contacts_provider():
    with patch.object(smoke, "request") as request:
        report = smoke.observe("secret")
    request.assert_not_called()
    assert not report["inference_attempted"]
    assert report["reason"] == "explicit_smoke_not_requested"


def test_missing_secret_never_contacts_provider():
    with patch.object(smoke, "request") as request:
        report = smoke.observe(None, execute=True)
    request.assert_not_called()
    assert report["reason"] == "missing_secret"


@pytest.mark.parametrize("account", [{}, {"data": {}}, {"data": {"is_free_tier": False}}, {"data": {"is_free_tier": 1}}, {"data": {"is_free_tier": "true"}}])
def test_token_and_catalog_never_imply_free_account(account):
    report, request = run(account=account)
    assert request.call_count == 1
    assert report["reason"] == "free_account_unverified"
    assert not report["inference_attempted"]


@pytest.mark.parametrize("pricing", [{}, {"prompt": "0"}, {"prompt": "0", "completion": ".1"}, {"prompt": "0", "completion": "0", "request": "1"}, {"prompt": "NaN", "completion": "0"}, {"prompt": False, "completion": "0"}, {"prompt": None, "completion": "0"}, {"prompt": "-1", "completion": "0"}])
def test_nonzero_or_incomplete_pricing_blocks_all_posts(pricing):
    report, request = run(catalog={"data": [model(pricing)]})
    assert request.call_count == 2
    assert report["reason"] == "exact_zero_price_model_unverified"
    assert not report["inference_attempted"]


@pytest.mark.parametrize("rows", [[], [model(), model()], [{"id": "another/model:free", "pricing": {"prompt": "0", "completion": "0"}}]])
def test_missing_ambiguous_or_other_exact_model_is_not_selected(rows):
    report, request = run(catalog={"data": rows})
    assert request.call_count == 2
    assert not report["inference_attempted"]


def test_one_bounded_smoke_with_zero_price_no_fallback():
    report, request = run()
    assert report["inference_ok"]
    assert report["completion_requests"] == 1
    assert request.call_count == 3
    args = request.call_args.args
    assert args[:2] == ("/chat/completions", "never-serialize-secret")
    payload = args[2]
    assert payload["model"] == smoke.MODEL
    assert payload["max_tokens"] == 16
    assert payload["stream"] is False
    assert "models" not in payload and "plugins" not in payload and "tools" not in payload
    assert payload["provider"] == {"allow_fallbacks": False, "require_parameters": True, "max_price": {"prompt": 0, "completion": 0, "request": 0, "image": 0}}
    assert "never-serialize-secret" not in json.dumps(report)
    assert report["production_admission_changed"] is False


@pytest.mark.parametrize("completion", [{}, {"model": "other", "choices": [{"message": {"content": "OK"}}]}, {"model": smoke.MODEL, "choices": [{"message": {"content": "private-provider-text"}}]}, {"model": smoke.MODEL, "choices": [{"message": {"content": "OK"}}], "usage": {"cost": ".1"}}, {"model": smoke.MODEL, "choices": [{"message": {"content": "OK"}}]}])
def test_invalid_completion_or_cost_never_claims_success(completion):
    report, request = run(completion=completion)
    assert request.call_count == 3
    assert not report["inference_ok"]
    assert "private-provider-text" not in json.dumps(report)


def test_error_no_retry_no_body_no_token():
    error = urllib.error.HTTPError("https://private?key=secret", 429, "private", {}, None)
    with patch.object(smoke, "request", side_effect=[{"data": {"is_free_tier": True}}, {"data": [model()]}, error]) as request:
        report = smoke.observe("never-leak", execute=True)
    assert request.call_count == 3
    assert report["completion_requests"] == 1
    assert report["reason"] == "inference_http_429"
    assert "private" not in json.dumps(report) and "never-leak" not in json.dumps(report)


def test_account_labels_balances_and_ids_are_not_evidence():
    account = {"data": {"is_free_tier": True, "label": "PRIVATE_ACCOUNT_LABEL", "limit_remaining": 12345, "hash": "PRIVATE_ACCOUNT_ID"}}
    report, _ = run(account=account)
    assert report["inference_ok"]
    assert "PRIVATE" not in json.dumps(report) and "12345" not in json.dumps(report)


def test_transport_is_bounded_and_redirects_refused():
    assert smoke.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.invalid") is None
    with pytest.raises(ValueError, match="invalid_endpoint"):
        smoke.request("https://evil.invalid", "secret")


def test_cli_requires_explicit_execution(tmp_path):
    path = tmp_path / "receipt.json"
    with patch.object(smoke, "request") as request:
        assert smoke.main(["--output", str(path)]) == 0
    request.assert_not_called()
    assert json.loads(path.read_text())["completion_requests"] == 0


def test_smoke_workflow_is_explicit_default_branch_only_and_secret_scoped():
    from pathlib import Path
    import yaml
    workflow = yaml.safe_load((Path(__file__).resolve().parents[1] / '.github/workflows/provider-batch.yml').read_text())
    events = workflow.get('on', workflow.get(True))
    assert events['workflow_dispatch']['inputs']['execute_free_smoke']['default'] is False
    assert 'github.event.repository.default_branch' in workflow['jobs']['observe']['if']
    step = next(s for s in workflow['jobs']['observe']['steps'] if s.get('name') == 'Execute one explicitly requested verified no-cost smoke')
    assert step['if'] == 'inputs.execute_free_smoke'
    assert set(step['env']) == {'OPENROUTER_API_KEY'}
    assert '--execute' in step['run']


def test_scheduled_availability_is_catalog_only():
    from pathlib import Path
    import yaml
    workflow = yaml.safe_load((Path(__file__).resolve().parents[1] / '.github/workflows/provider-availability.yml').read_text())
    script = next(s['run'] for s in workflow['jobs']['probe']['steps'] if s.get('name') == 'Validate configured-provider continuity')
    assert 'ok=p["catalog_ok"]' in script
    assert 'required_inference=' not in script
