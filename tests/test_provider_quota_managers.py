import json
import tempfile
import unittest
from pathlib import Path

from scripts import provider_quota_managers as managers
from scripts.provider_quota_coverage import _providers


class ProviderQuotaManagerTests(unittest.TestCase):
    def test_registry_is_exhaustive_and_explicit(self):
        rows = managers.load_managers()
        self.assertEqual(set(rows), set(_providers()))
        self.assertEqual(len(rows), 27)
        self.assertTrue(all(r['status'] in {'implemented_passive_adapter', 'public_documentation_only', 'unsupported'} for r in rows.values()))

    def test_public_metadata_is_static_and_has_no_account_values(self):
        result = managers.build_public_metadata()
        self.assertFalse(result['network_used'])
        self.assertFalse(result['live_account_validation'])
        self.assertEqual(result['runtime_admission'], 'unchanged')
        self.assertTrue(all('signals' not in r or isinstance(r['signals'], list) for r in result['provider_families']))
        self.assertTrue(all('observations' not in row and 'quota_values' not in row for row in result['provider_families']))

    def test_groq_header_normalization_is_private_and_metric_scoped(self):
        obs = managers.normalize_observation(
            'groq',
            {'X-RateLimit-Limit-Requests': '120', 'x-ratelimit-remaining-requests': '119',
             'x-ratelimit-reset-requests': '2m59.56s', 'Authorization': 'secret'},
            observed_at='2026-10-21T09:00:00Z', scope='organization:model=sample',
        )
        self.assertEqual(obs['signals']['limit_requests'], 120)
        self.assertEqual(obs['signals']['remaining_requests'], 119)
        self.assertEqual(obs['scope_status'], 'caller_declared_unverified')
        self.assertNotIn('secret', json.dumps(obs))
        self.assertAlmostEqual(obs['signals']['reset_after_requests'], 179.56)

    def test_openrouter_metadata_allowlist_and_timestamp(self):
        obs = managers.normalize_observation(
            'openrouter', metadata={'data': {'limit_remaining': 1.25, 'free_model_daily_requests': {'used': 7, 'limit': 50, 'remaining': 43}}},
            observed_at='2026-10-21T02:00:00-07:00', scope='API key',
        )
        self.assertEqual(obs['observed_at'], '2026-10-21T09:00:00Z')
        self.assertEqual(obs['signals']['limit_remaining'], 1.25)
        self.assertEqual(obs['signals']['free_model_daily_remaining'], 43)
        self.assertNotIn('reset_at', obs['signals'])

    def test_rejects_bad_scope_timestamp_and_numeric_values(self):
        base = {'provider_family': 'groq', 'headers': {'x-ratelimit-remaining-requests': 'NaN'},
                'observed_at': '2026-10-21T09:00:00Z', 'scope': 'org'}
        with self.assertRaises(ValueError):
            managers.normalize_observation(base['provider_family'], base['headers'], observed_at=base['observed_at'], scope=base['scope'])
        for raw in ['1.5', '9' * 10000]:
            with self.assertRaises(ValueError):
                managers.normalize_observation('groq', {'x-ratelimit-remaining-requests': raw},
                                               observed_at='2026-10-21T09:00:00Z', scope='org')
        for timestamp, scope in [('2026-10-21T09:00:00', 'org'), ('2026-10-21T09:00:00Z', ''),
                                 ('0001-01-01T00:00:00+23:59', 'org'), ('9999-12-31T23:59:59-23:59', 'org')]:
            with self.assertRaises(ValueError):
                managers.normalize_observation('groq', {}, observed_at=timestamp, scope=scope)

    def test_unsupported_family_fails_closed(self):
        with self.assertRaises(ValueError):
            managers.normalize_observation('cohere', {}, observed_at='2026-10-21T09:00:00Z', scope='key')

    def test_sambanova_does_not_assume_reset_header_units(self):
        obs = managers.normalize_observation('sambanova', {
            'x-ratelimit-limit-requests': '20', 'x-ratelimit-remaining-requests': '19',
            'x-ratelimit-reset-requests': '60', 'x-ratelimit-reset-requests-day': '1m'},
            observed_at='2026-10-21T09:00:00Z', scope='user/model')
        self.assertEqual(obs['signals'], {'limit_requests': 20, 'remaining_requests': 19})
        self.assertNotIn('reset_at', obs)

    def test_duplicate_rows_rejected(self):
        data = {'schema': 'provider-quota-managers/v1', 'provider_families': [
            {'provider_family': 'x'}, {'provider_family': 'x'}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'managers.json'
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                managers.load_managers(path)

    def test_public_metadata_drops_unknown_nested_signal_canaries(self):
        data = {'schema': 'provider-quota-managers/v1', 'provider_families': [
            {'provider_family': 'test', 'status': 'implemented_passive_adapter',
             'source': 'https://example.org/docs', 'scope': 'test', 'reset': 'unknown',
             'signals': [{'field': 'api_key', 'value': 'private-canary-123', 'header': 'Authorization'},
                         {'field': 'remaining_requests', 'value': 'must-not-leak', 'header': 'x-rate-limit-rem'}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'managers.json'
            path.write_text(json.dumps(data))
            result = managers.build_public_metadata(path)
        encoded = json.dumps(result)
        self.assertNotIn('private-canary-123', encoded)
        self.assertNotIn('must-not-leak', encoded)
        self.assertNotIn('Authorization', encoded)
        self.assertEqual(result['provider_families'][0]['signals'], [{'field': 'remaining_requests', 'header': 'x-rate-limit-rem'}])

    def test_siliconflow_preserves_private_monetary_decimal_strings_not_quota(self):
        obs = managers.normalize_observation('siliconflow', metadata={'data': {
            'balance': '0.88', 'chargeBalance': '88.00', 'totalBalance': '88.88',
            'email': 'private-email-canary', 'id': 'private-account-canary'}},
            observed_at='2026-10-21T09:00:00Z', scope='user')
        self.assertEqual(obs['signals'], {'monetary_balance': '0.88', 'monetary_charge_balance': '88.00', 'monetary_total_balance': '88.88'})
        self.assertNotIn('canary', json.dumps(obs))
        self.assertNotIn('remaining_requests', obs['signals'])
        for raw in [True, 0.88, 'NaN', '-1', 'Infinity']:
            with self.assertRaises(ValueError):
                managers.normalize_observation('siliconflow', metadata={'data': {'balance': raw}},
                    observed_at='2026-10-21T09:00:00Z', scope='user')

    def test_inconsistent_or_partial_counter_and_bad_mapping_are_rejected(self):
        for raw in [{'used': 8}, {'used': 8, 'limit': 50, 'remaining': 43}]:
            with self.assertRaises(ValueError):
                managers.normalize_observation('openrouter', metadata={'data': {'free_model_daily_requests': raw}},
                    observed_at='2026-10-21T09:00:00Z', scope='account')
        with self.assertRaises(ValueError):
            managers.normalize_observation('groq', {'x-ratelimit-limit-requests': '1', 'x-ratelimit-remaining-requests': '2'},
                observed_at='2026-10-21T09:00:00Z', scope='org')
        with self.assertRaises(ValueError):
            managers.normalize_observation('groq', ['not-a-header-mapping'], observed_at='2026-10-21T09:00:00Z', scope='org')

    def test_catalog_status_is_status_only_and_unknown_by_default_for_every_family(self):
        for family in managers.load_managers():
            result = managers.catalog_quota_status(family,
                {'x-ratelimit-remaining-requests': 'secret-canary'}, observed_at='2026-10-21T09:00:00Z')
            self.assertEqual(result['status'], 'unknown', family)
            self.assertEqual(set(result), {'status', 'manager_status'})
        self.assertEqual(managers.catalog_quota_status('unregistered', {}, observed_at='2026-10-21T09:00:00Z'),
                         {'status': 'unknown', 'manager_status': 'unsupported'})
        encoded = json.dumps(managers.catalog_quota_status('groq',
            {'x-ratelimit-remaining-requests': 'secret-canary'}, observed_at='2026-10-21T09:00:00Z'))
        self.assertNotIn('secret-canary', encoded)
        self.assertNotIn('scope', encoded)

    def test_catalog_status_accepts_only_applicable_documented_headers_and_fails_closed(self):
        at = '2026-10-21T09:00:00Z'
        groq = managers.catalog_quota_status('groq',
            {'x-ratelimit-remaining-requests': '119'}, observed_at=at,
            source='https://api.groq.com/openai/v1/models')
        self.assertEqual(groq['status'], 'observed')
        bad = managers.catalog_quota_status('groq',
            {'x-ratelimit-remaining-requests': 'bearer-secret'}, observed_at=at,
            source='https://api.groq.com/openai/v1/models')
        self.assertEqual(bad['status'], 'unknown')
        samba = managers.catalog_quota_status('sambanova',
            {'x-ratelimit-remaining-requests': '19'}, observed_at=at,
            source='https://api.sambanova.ai/v1/models')
        self.assertEqual(samba['status'], 'observed')
        # HF Hub RateLimit does not describe the Hugging Face inference router.
        self.assertEqual(managers.catalog_quota_status('huggingface',
            {'ratelimit': 'r=1;t=2'}, observed_at=at)['status'], 'unknown')

    def test_catalog_status_rejects_missing_or_mismatched_origin(self):
        for family in ('groq', 'sambanova'):
            for source in (None, 'https://untrusted.invalid/v1/models',
                           'https://openapi.felo.ai/api/v1/models'):
                result = managers.catalog_quota_status(family,
                    {'x-ratelimit-remaining-requests': '19'},
                    observed_at='2026-10-21T09:00:00Z', source=source)
                self.assertEqual(result['status'], 'unknown')

    def test_catalog_logs_status_not_raw_header_values(self):
        import contextlib
        import io
        from unittest.mock import patch
        from scripts import provider_model_catalog as catalog
        row = {'id': 'test', 'provider': 'groq', 'pricing_classification': 'paid',
               'free_suffix': False, 'access_classification': 'catalog_pricing_only'}
        log = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(log), \
             patch.object(catalog, 'resolve_secret', return_value=('token-canary', 'GROQ_API_KEY')), \
             patch.object(catalog, 'poll', return_value=([row], {'x-request-id': 'opaque-header-canary'})):
            self.assertEqual(catalog.main(['--providers', 'groq', '--output', str(Path(tmp) / 'catalog.json')]), 0)
        self.assertIn('QUOTA_STATUS groq:', log.getvalue())
        self.assertNotIn('opaque-header-canary', log.getvalue())
        self.assertNotIn('token-canary', log.getvalue())

    def test_catalog_main_includes_projection_without_changing_catalog_fields(self):
        from unittest.mock import patch
        from scripts import provider_model_catalog as catalog
        payload = {'data': [{'id': 'example'}]}
        with tempfile.TemporaryDirectory() as tmp, patch.object(catalog, 'resolve_secret', return_value=('token-canary', 'GROQ_API_KEY')), \
             patch.object(catalog, 'poll', return_value=([{'id': 'test', 'provider': 'groq', 'pricing_classification': 'paid', 'free_suffix': False, 'access_classification': 'catalog_pricing_only'}], {'x-ratelimit-remaining-requests': '5'})):
            out = Path(tmp) / 'catalog.json'
            self.assertEqual(catalog.main(['--providers', 'groq', '--output', str(out)]), 0)
            data = json.loads(out.read_text())
        observation = data['provider_observations']['groq']
        self.assertEqual(observation['response_headers'], {'x-ratelimit-remaining-requests': '5'})
        self.assertEqual(observation['quota_manager'], {'status': 'observed', 'manager_status': 'implemented_passive_adapter'})
        self.assertNotIn('token-canary', json.dumps(observation['quota_manager']))


if __name__ == '__main__':
    unittest.main()
