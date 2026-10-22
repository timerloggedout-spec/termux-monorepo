import datetime as dt
import json
import multiprocessing
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from llm_api_hub.server.admission import AdmissionDenied, QuotaAdmission, bind_canonical_observation


def evidence(tmp_path, **updates):
    now = dt.datetime.now(dt.timezone.utc)
    row = {"account": "acct-fixture", "provider": "openrouter", "model": "openrouter/model-fixture",
           "evidence_status": "confirmed", "horizon": "H0", "free_account_verified": True,
           "scope": "shared-account", "observed_at": now.isoformat(),
           "reset_at": (now + dt.timedelta(hours=1)).isoformat(), "remaining": 1}
    row.update(updates)
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"schema_version": 1, "records": [row]}), encoding="utf-8")
    return path


def test_unknown_exhausted_unverified_and_invalid_amounts(tmp_path):
    manager = QuotaAdmission(db_path=tmp_path / "q.sqlite")
    with pytest.raises(AdmissionDenied, match="quota_unknown"):
        manager.reserve("openrouter", "openrouter/model-fixture")
    manager = QuotaAdmission(records_path=evidence(tmp_path, remaining=0), db_path=tmp_path / "q.sqlite")
    with pytest.raises(AdmissionDenied):
        manager.reserve("openrouter", "openrouter/model-fixture")
    manager = QuotaAdmission(records_path=evidence(tmp_path, free_account_verified=False), db_path=tmp_path / "q.sqlite")
    with pytest.raises(AdmissionDenied):
        manager.reserve("openrouter", "openrouter/model-fixture")
    manager = QuotaAdmission(records_path=evidence(tmp_path), db_path=tmp_path / "q.sqlite")
    for value in (-1, True, float("nan"), float("inf")):
        with pytest.raises(AdmissionDenied):
            manager.reserve("openrouter", "openrouter/model-fixture", amount=value)


def test_thread_atomicity_and_ambiguous_is_charged(tmp_path):
    manager = QuotaAdmission(records_path=evidence(tmp_path), db_path=tmp_path / "q.sqlite")
    def attempt(_):
        try:
            return manager.reserve("openrouter", "openrouter/model-fixture")
        except AdmissionDenied:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = [v for v in pool.map(attempt, range(8)) if v]
    assert len(accepted) == 1
    manager.mark_sent(accepted[0])
    assert manager.reconcile(accepted[0], ambiguous=True) == "charged"
    with pytest.raises(AdmissionDenied):
        manager.reserve("openrouter", "openrouter/model-fixture")


def _process_reserve(records, db, output):
    try:
        output.put(QuotaAdmission(records, db).reserve("openrouter", "openrouter/model-fixture"))
    except AdmissionDenied:
        output.put(None)


def test_process_atomicity_and_restart_conservative(tmp_path):
    records, db = evidence(tmp_path), tmp_path / "shared.sqlite"
    ctx = multiprocessing.get_context("fork")
    q = ctx.Queue()
    ps = [ctx.Process(target=_process_reserve, args=(str(records), str(db), q)) for _ in range(6)]
    for p in ps: p.start()
    for p in ps: p.join()
    accepted = [q.get() for _ in ps]
    token = next(x for x in accepted if x)
    assert sum(x is not None for x in accepted) == 1
    QuotaAdmission(records, db).mark_sent(token)
    # A new process/instance has no grounds to release an in-flight send.
    mgr = QuotaAdmission(records, db)
    assert mgr.reconcile(token, actual=0) == "charged"


def test_duplicate_attempt_blocks_repeat_dispatch_and_unsent_release(tmp_path):
    mgr = QuotaAdmission(evidence(tmp_path), tmp_path / "q.sqlite")
    token = mgr.reserve("openrouter", "openrouter/model-fixture", attempt_id="attempt-1")
    with pytest.raises(AdmissionDenied, match="duplicate_attempt"):
        mgr.reserve("openrouter", "openrouter/model-fixture", attempt_id="attempt-1")
    assert mgr.reconcile(token, actual=0) == "released"


def test_cooldown_persists_and_refresh_does_not_release_inflight(tmp_path):
    records, db = evidence(tmp_path), tmp_path / "q.sqlite"
    mgr = QuotaAdmission(records, db)
    token = mgr.reserve("openrouter", "openrouter/model-fixture")
    mgr.mark_sent(token)
    mgr.add_cooldown(token, 90)
    # A fresh observation refresh is not evidence the earlier in-flight request was unused.
    records = evidence(tmp_path, observed_at=dt.datetime.now(dt.timezone.utc).isoformat(), remaining=1)
    mgr = QuotaAdmission(records, db)
    with pytest.raises(AdmissionDenied, match="cooldown"):
        mgr.reserve("openrouter", "openrouter/model-fixture")
    assert mgr.reconcile(token, ambiguous=True) == "charged"
    with pytest.raises(AdmissionDenied):
        mgr.reserve("openrouter", "openrouter/model-fixture")


def test_reset_requires_fresh_canonical_window(tmp_path):
    old_reset = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=2)).isoformat()
    mgr = QuotaAdmission(evidence(tmp_path, reset_at=old_reset), tmp_path / "q.sqlite")
    with pytest.raises(AdmissionDenied, match="reset_refresh"):
        mgr.reserve("openrouter", "openrouter/model-fixture")


def test_actual_tokens_partial_and_unknown_usage_hold_reservation(tmp_path):
    records, db = evidence(tmp_path, remaining=3, remaining_tokens=100), tmp_path / "q.sqlite"
    mgr = QuotaAdmission(records, db)
    first = mgr.reserve("openrouter", "openrouter/model-fixture", token_budget=60)
    mgr.mark_sent(first)
    assert mgr.reconcile(first, actual=1, actual_tokens=17) == "charged"
    second = mgr.reserve("openrouter", "openrouter/model-fixture", token_budget=80)
    mgr.mark_sent(second)
    assert mgr.reconcile(second, actual=None, actual_tokens=None, ambiguous=True) == "charged"
    with pytest.raises(AdmissionDenied, match="token_quota"):
        mgr.reserve("openrouter", "openrouter/model-fixture", token_budget=5)


def test_shared_scope_across_models_and_binding_checks():
    obs = {"status": "observed", "scope": "account", "scope_status": "caller_declared_unverified",
           "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "provider_family": "p", "signals": {"remaining_requests": 2}}
    with pytest.raises(AdmissionDenied):
        bind_canonical_observation(obs, account_id="acct", provider="p", model="m",
                                  remaining_field="remaining_requests", reset_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                                  verified_account=True, verified_free_account=True)
    bound = bind_canonical_observation(obs, account_id="acct", provider="p", model="m",
          remaining_field="remaining_requests", reset_at=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=1)).isoformat(),
          verified_account=True, verified_free_account=True, provider_model_mapping={"m": "p"})
    assert bound["free_account_verified"] is True


def test_refresh_drifting_reset_does_not_reset_inflight_usage(tmp_path):
    path = evidence(tmp_path, remaining=1)
    manager = QuotaAdmission(path, tmp_path / 'q.sqlite')
    token = manager.reserve('openrouter', 'openrouter/model-fixture', attempt_id='original')
    manager.mark_sent(token)
    # A new observation's relative reset differs by milliseconds, not by a window.
    evidence(tmp_path, remaining=1)
    with pytest.raises(AdmissionDenied, match='quota_exhausted'):
        QuotaAdmission(path, manager.db_path).reserve('openrouter', 'openrouter/model-fixture', attempt_id='refresh')


def test_same_account_scope_is_shared_across_exact_models(tmp_path):
    path = evidence(tmp_path, remaining=1)
    doc = json.loads(path.read_text())
    other = dict(doc['records'][0], model='openrouter/other-model')
    doc['records'].append(other)
    path.write_text(json.dumps(doc))
    manager = QuotaAdmission(path, tmp_path / 'shared.sqlite')
    manager.reserve('openrouter', 'openrouter/model-fixture')
    with pytest.raises(AdmissionDenied, match='quota_exhausted'):
        manager.reserve('openrouter', 'openrouter/other-model')


def test_canonical_publication_is_private_and_retains_other_models(tmp_path):
    from llm_api_hub.server.quota_observations import publish_observation
    now = dt.datetime.now(dt.timezone.utc)
    observation = {'provider_family': 'p', 'status': 'observed', 'scope': 'account',
                   'scope_status': 'caller_declared_unverified', 'observed_at': now.isoformat(),
                   'signals': {'remaining_requests': 2, 'authorization': 'never-persist'}}
    binding = dict(account_id='fixture-account', provider='p', model='p/one', remaining_field='remaining_requests',
                   reset_at=(now+dt.timedelta(hours=1)).isoformat(), verified_account=True,
                   verified_free_account=True, provider_model_mapping={'p/one': 'p', 'p/two': 'p'})
    path = tmp_path / 'private' / 'source.json'
    publish_observation(path, observation, **binding)
    publish_observation(path, observation, **dict(binding, model='p/two'))
    assert len(json.loads(path.read_text())['records']) == 2
    assert path.stat().st_mode & 0o777 == 0o600
    assert 'never-persist' not in path.read_text()
    manager = QuotaAdmission(path, tmp_path / 'shared.sqlite')
    assert manager.reserve('p', 'p/one')
    assert manager.reserve('p', 'p/two')
    with pytest.raises(AdmissionDenied): manager.reserve('p', 'p/one')
    with pytest.raises(AdmissionDenied): publish_observation(path, observation, **dict(binding, verified_account='true'))
    with pytest.raises(AdmissionDenied): publish_observation(path, observation, **dict(binding, account_id='another-account'))


def test_model_fanout_cannot_expand_shared_scope_signal(tmp_path):
    path = evidence(tmp_path, remaining=2)
    doc = json.loads(path.read_text())
    doc['records'].append(dict(doc['records'][0], model='openrouter/large', remaining=100))
    path.write_text(json.dumps(doc))
    manager = QuotaAdmission(path, tmp_path / 'shared.sqlite')
    manager.reserve('openrouter', 'openrouter/large')
    manager.reserve('openrouter', 'openrouter/large')
    with pytest.raises(AdmissionDenied, match='quota_exhausted'):
        manager.reserve('openrouter', 'openrouter/large')


def test_expired_window_requires_observation_after_that_window(tmp_path):
    import time
    path = evidence(tmp_path, remaining=2)
    manager = QuotaAdmission(path, tmp_path / 'reset.sqlite')
    manager.reserve('openrouter', 'openrouter/model-fixture')
    # Simulate passage of the known window, while the source is still an old
    # observation with an incorrectly extended future reset.
    with sqlite3.connect(manager.db_path) as db:
        db.execute('UPDATE quota_windows SET reset_at=?', (time.time()-1,))
    doc = json.loads(path.read_text())
    doc['records'][0]['observed_at'] = (dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=2)).isoformat()
    path.write_text(json.dumps(doc))
    with pytest.raises(AdmissionDenied, match='quota_reset_refresh_required'):
        manager.reserve('openrouter', 'openrouter/model-fixture')
    evidence(tmp_path, remaining=2)
    assert manager.reserve('openrouter', 'openrouter/model-fixture')
