import datetime as dt
import sys
import types
from scripts.provider_quota_mapping import capability, observe_family, service_capability


def test_mapping_classifies_runtime_passive_sources_and_unknowns_explicitly():
    assert capability("groq")["status"] == "implemented_passive_parser"
    assert capability("huggingface")["dimensions"] == "hub_api_requests_only"
    assert capability("gemini")["status"] == "documentation_only"
    assert capability("provider-not-in-roster")["status"] == "unsupported_or_unknown"
    for family in ("groq", "huggingface", "gemini", "provider-not-in-roster"):
        row = capability(family)
        assert row["fail_closed"] is True
        assert row["remaining"] == "not_observed"
        assert row["freshness"] == "unknown_until_timestamped_observation"
        assert row["entitlement"]


def test_siliconflow_is_monetary_only():
    row = capability("siliconflow")
    assert row["status"] == "unsupported_live_source_historical_parser"
    assert row["dimensions"] == "historical_monetary_balance_only_not_request_quota"
    assert row["remaining"] == "not_observed" and row["fail_closed"] is True


def test_gemini_requires_both_registered_manager_and_callable_parser(monkeypatch):
    registered = {"status": "implemented_passive_adapter"}
    monkeypatch.setitem(sys.modules, "scripts.provider_quota_gemini", None)
    assert capability("gemini", registered)["status"] == "documentation_only"
    module = types.ModuleType("scripts.provider_quota_gemini")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert capability("gemini", registered)["parser_available"] is False
    module.normalize_gemini_evidence = lambda **kwargs: {}
    assert capability("gemini", {"status": "public_documentation_only"})["parser_available"] is False
    row = capability("gemini", registered)
    assert row["status"] == "implemented_passive_parser"
    assert row["source_kind"] == "caller_supplied_private_evidence"
    assert row["dimensions"] == "project_model_rpm_input_tpm_rpd"
    assert row["parser_available"] is True and row["remaining"] == "not_observed"
    # This internal envelope is not a provider endpoint response contract.
    result = observe_family("gemini", source="https://ai.google.dev/gemini-api/docs/rate-limits",
                            observed_at="2025-01-01T00:00:00Z", scope="synthetic")
    assert result["status"] == "unknown" and result["reason"] == "unsupported_source"
    assert result["runtime_admission"] == "unchanged"


def test_nonmodel_services_get_typed_unknown_contract():
    row = service_capability({"unit": "GB", "lane": "data", "reset": "monthly"})
    assert row["status"] == "unknown_unless_explicit_reader_registered"
    assert row["dimension"] == "GB" and row["scope"] == "data" and row["fail_closed"] is True


def test_dispatcher_uses_only_allowlisted_endpoint_and_normalizer():
    now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    valid = observe_family("groq", source="https://api.groq.com/openai/v1/models",
        observed_at="2025-01-01T00:00:00Z", now=now, scope="org/model",
        headers={"x-ratelimit-limit-requests": "100", "x-ratelimit-remaining-requests": "90"})
    assert valid["status"] == "observed" and valid["runtime_admission"] == "unchanged"
    assert valid["remaining"] == "not_observed" and valid["entitlement"] == "unknown"
    result = observe_family("huggingface", source="https://router.huggingface.co/v1",
        observed_at="2025-01-01T00:00:00Z", now=now, scope="Hub API")
    assert result["status"] == "unknown" and result["reason"] == "source_not_allowlisted_for_family"
    empty = observe_family("huggingface", source="https://huggingface.co/api/models",
        observed_at="2025-01-01T00:00:00Z", now=now, scope="Hub API")
    assert empty["status"] == "unknown" and empty["reason"] == "no_signals"


def test_dispatcher_rejects_future_stale_missing_scope_and_unbounded_ttl():
    now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    base = dict(family="groq", source="https://api.groq.com/openai/v1/models", now=now,
                scope="declared org/model", headers={"x-ratelimit-remaining-requests": "9"})
    assert observe_family(**base, observed_at="2025-01-01T00:00:01Z")["reason"] == "future_timestamp"
    assert observe_family(**base, observed_at="2024-12-31T23:58:59Z")["reason"] == "stale_timestamp"
    assert observe_family(**{**base, "scope": None}, observed_at="2025-01-01T00:00:00Z")["reason"] == "scope_required"
    assert observe_family(**base, observed_at="2025-01-01T00:00:00Z", ttl_seconds=61)["reason"] == "invalid_ttl"


def test_actions_operational_dimensions_are_documented_not_live_account_quotas():
    import json
    from pathlib import Path
    rows = {r['id']: r for r in json.loads(Path('ops/quota/registry.json').read_text())['services']}
    expected = {'workflow_runtime': 35, 'approval_wait': 30, 'matrix_jobs': 256,
                'trigger_events': 1500, 'queued_runs': 500, 'concurrency_queue_max': 100,
                'hosted_job_runtime': 6, 'self_hosted_job_runtime': 5, 'self_hosted_queue_wait': 24}
    for suffix, ceiling in expected.items():
        row = rows['github.actions.' + suffix]
        assert row['limit'] == ceiling
        assert row['source'] == 'https://docs.github.com/en/actions/reference/limits'
        assert row['lane'] == 'ci-policy'
        assert row['remaining_state'] == row['observation_state'] == 'unknown'
        capability_row = service_capability(row)
        assert capability_row['fail_closed'] is True
        assert capability_row['status'] == 'unknown_unless_explicit_reader_registered'
    assert rows['github.actions.hosted_concurrency']['limit'] is None
    assert rows['github.actions.hosted_macos_concurrency']['limit'] is None
    assert 'queue: max' in rows['github.actions.concurrency_queue_max']['metric']


def test_passive_validity_expires_at_source_reset_and_never_after_ttl():
    now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    base = dict(family='groq', source='https://api.groq.com/openai/v1/models',
                observed_at=now.isoformat(), scope='declared:org',
                headers={'x-ratelimit-remaining-requests': '9', 'x-ratelimit-reset-requests': '5s'})
    fresh = observe_family(**base, now=now)
    assert dt.datetime.fromisoformat(fresh['valid_until']) == now + dt.timedelta(seconds=5)
    expired = observe_family(**base, now=now + dt.timedelta(seconds=5))
    assert expired['status'] == 'unknown' and expired['signals'] == {}
    assert expired['reason'] == 'source_reset_due_refresh_required'
    for bad in (None, 12, []):
        assert observe_family(**{**base, 'observed_at': bad}, now=now)['status'] == 'unknown'
    assert observe_family(**base, now='not-a-date')['reason'] == 'invalid_now'
    assert observe_family(**base, now=now + dt.timedelta(seconds=60))['reason'] == 'stale_timestamp'


def test_source_error_payload_never_becomes_siliconflow_balance_evidence():
    result = observe_family('siliconflow', source='https://api.siliconflow.com/v1/user/info',
                            observed_at='2025-01-01T00:00:00Z', now=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                            scope='declared:user', metadata={'status': False, 'code': 50000, 'data': {'balance': '1'}})
    assert result['status'] == 'unknown' and result['signals'] == {}


def test_all_existing_pollers_have_typed_dimension_specific_reader_mappings():
    import json
    from pathlib import Path
    from scripts import quota_poll
    rows = json.loads(Path('ops/quota/registry.json').read_text())['services']
    for row in rows:
        if row['id'] in quota_poll.LIVE or row['id'] in {'render.bandwidth', 'render.pipeline_minutes', 'neon.compute', 'neon.storage'}:
            typed = service_capability(row)
            assert typed['status'] == 'typed_reader' and typed['reader']
            assert typed['remaining'] == 'not_observed_by_public_coverage_inventory'


def test_every_declared_executable_reader_resolves_to_a_callable():
    import importlib
    import json
    from pathlib import Path
    for row in json.loads(Path('ops/quota/registry.json').read_text())['services']:
        reader = service_capability(row)['reader']
        if reader:
            module, symbol = reader.rsplit('.', 1)
            assert callable(getattr(importlib.import_module(module), symbol, None)), reader


def test_documented_secondary_policies_do_not_invent_live_remaining_capacity():
    import json
    from pathlib import Path
    rows = {r['id']: r for r in json.loads(Path('ops/quota/registry.json').read_text())['services']}
    expected = {'concurrent_requests': 100, 'rest_points': 900, 'graphql_points': 2000,
                'cpu_total': 90, 'cpu_graphql': 60, 'content_minute': 80,
                'content_hour': 500, 'oauth_token_requests': 2000}
    for suffix, threshold in expected.items():
        row = rows['github.api.secondary.' + suffix]
        assert row['limit'] == threshold and row['lane'] == 'api-policy'
        assert row['remaining_state'] == row['observation_state'] == 'unknown'
        assert service_capability(row)['reader'] is None
        assert 'secondary reset not exposed' in row['reset']
