import json, threading, time, urllib.error
import pytest
from scripts import github_quota_manager as gm

def payload(now=None):
    now=int(time.time() if now is None else now); rate={"limit":5000,"remaining":4500,"used":500,"reset":now+3600}
    return {"resources":{"core":rate,"search":rate,"graphql":rate,"integration_manifest":rate,"not_allowlisted":{"token":"secret"}}}
class Response:
    status=200; headers={}
    def __init__(self, body=None, url=gm.API_URL): self.body=body or json.dumps(payload()).encode(); self.url=url
    def __enter__(self): return self
    def __exit__(self,*a): pass
    def read(self,n): return self.body
    def geturl(self): return self.url

def test_allowlist_private_data_and_class_is_explicit():
    r=gm.normalize(payload(),token_class="github_token")
    assert r["token_class"]=="github_token" and r["resources"]["integration_manifest"]["remaining"]==4500
    assert "not_allowlisted" not in r["resources"] and r["actions_product_quotas"]=="unknown"
    assert gm.normalize(payload())["token_class"]=="unknown"
    with pytest.raises(gm.QuotaError): gm.normalize(payload(),token_class="whatever")
@pytest.mark.parametrize("mutate",[lambda p:p.clear(),lambda p:p["resources"].pop("core"),lambda p:p["resources"]["core"].update(remaining=True),lambda p:p["resources"]["search"].update(reset=int(time.time())-1),lambda p:p["resources"]["graphql"].update(remaining=5001)])
def test_malformed_fails_closed(mutate):
    p=payload(); mutate(p)
    with pytest.raises(gm.QuotaError): gm.normalize(p)
def test_zero_limit_is_unknown_and_graphql_optional():
    p=payload(); p["resources"]["graphql"]={"limit":0,"remaining":0,"used":0,"reset":0}
    assert gm.normalize(p)["resources"]["graphql"] is None
    p["resources"].pop("graphql"); assert gm.normalize(p)["resources"]["graphql"] is None

def test_cache_separates_credentials_and_cli_is_status_only(monkeypatch):
    gm._cache.clear(); calls=[]
    def opener(req,timeout): calls.append(req.get_header("Authorization")); return Response()
    a=gm.observe("credential-A",opener=opener); b=gm.observe("credential-B",opener=opener)
    assert len(calls)==2 and a["resources"]==b["resources"] and "credential-A" not in json.dumps(a)
    assert gm._key("credential-A") != gm._key("credential-B")
    monkeypatch.setenv("GITHUB_TOKEN","private"); monkeypatch.setattr(gm, "observe", lambda *a, **k: a[0] and __import__("scripts.github_quota_manager", fromlist=["x"]).normalize(payload())); gm._cache.clear()
    from io import StringIO
    import contextlib
    output=StringIO()
    with contextlib.redirect_stdout(output): assert gm.main(["--observe"])==0
    text=output.getvalue(); assert "remaining" not in text and "reset" not in text and "private" not in text

def test_bounded_ttl():
    with pytest.raises(gm.QuotaError): gm.observe(opener=lambda *a,**k:None,cache_seconds=31)
    assert gm.MAX_TTL<=30

def test_no_unverified_host_or_path():
    for url in ("https://evil.example/rate_limit","https://api.github.com/other"):
        with pytest.raises(gm.QuotaError,match="unverified_response_target"): gm._request(None,lambda req,timeout:Response(url=url))
def test_http_error_backoff_honors_retry_after_and_no_retry():
    calls=[]; waits=[]
    def opener(*a,**k): calls.append(1); raise urllib.error.HTTPError(gm.API_URL,429,"private",{"Retry-After":"7"},None)
    with pytest.raises(gm.QuotaError,match="secondary_or_http_limited"): gm._request("secret",opener,sleeper=waits.append)
    assert calls==[1] and waits==[7]
    waits.clear()
    with pytest.raises(gm.QuotaError): gm._request(None,lambda *a,**k:(_ for _ in ()).throw(urllib.error.HTTPError(gm.API_URL,403,"x",{},None)),sleeper=waits.append)
    assert waits==[60]
def test_local_reserve_policy_is_explicit():
    assert gm.reserve_allows(1,100,10) and not gm.reserve_allows(1,10,10)
    assert not gm.reserve_allows(1,None,0)
    called=[]
    with pytest.raises(gm.QuotaError,match="local_reserve_threshold"):
        gm.observe("budget",opener=lambda *a,**k:called.append(1),remaining_budget=10,reserve=10)
    assert called==[]
    assert gm._key("same", "user_token") != gm._key("same", "github_token")
def test_concurrent_requests_coalesce():
    gm._cache.clear(); calls=[]; gate=threading.Event(); results=[]
    def opener(*a,**k): calls.append(1); gate.wait(1); return Response()
    threads=[threading.Thread(target=lambda:results.append(gm.observe("coalesce-token",opener=opener))) for _ in range(2)]
    for t in threads:t.start()
    time.sleep(.05); gate.set()
    for t in threads:t.join()
    assert len(calls)==1 and len(results)==2


def test_observed_secondary_throttle_blocks_subsequent_reads_without_retry():
    calls = []
    def limited(*args, **kwargs):
        calls.append(1)
        raise urllib.error.HTTPError(gm.API_URL, 429, 'private-error', {'Retry-After': '7'}, None)
    with pytest.raises(gm.QuotaError, match='secondary_or_http_limited'):
        gm.observe('cooldown-regression', opener=limited, sleeper=lambda _: None)
    with pytest.raises(gm.QuotaError, match='rate_limit_cooldown'):
        gm.observe('cooldown-regression', opener=limited, sleeper=lambda _: None)
    assert calls == [1]


def test_cache_is_immutable_and_bound_to_explicit_token_class_and_reset():
    calls = []
    now = int(time.time())
    def opener(*args, **kwargs):
        calls.append(1)
        return Response(json.dumps(payload(now)).encode())
    original = gm.observe('immutable-regression', opener=opener, now=now)
    original['resources']['core']['remaining'] = 0
    cached = gm.observe('immutable-regression', opener=opener, now=now)
    assert cached['resources']['core']['remaining'] == 4500 and len(calls) == 1
    assert cached['resources']['graphql']['dimension'] == 'points'
    assert cached['resources']['core']['dimension'] == 'requests'
    gm.observe('immutable-regression', opener=opener, now=now, token_class='user_token')
    assert len(calls) == 2


@pytest.mark.parametrize('bad', [True, float('nan'), float('inf'), -1, '5'])
def test_invalid_cache_policy_never_calls_transport(bad):
    with pytest.raises(gm.QuotaError):
        gm.observe('invalid-cache-regression', cache_seconds=bad,
                   opener=lambda *a, **k: pytest.fail('must not make a request'))


@pytest.mark.parametrize('bad', ['bad\ncredential', '', 123, 'x' * 4097])
def test_invalid_credential_never_calls_transport(bad):
    with pytest.raises(gm.QuotaError, match='invalid_credential'):
        gm.observe(bad, opener=lambda *a, **k: pytest.fail('must not make a request'))


def test_more_than_two_simultaneous_reads_share_one_success():
    calls = []; results = []; errors = []; gate = threading.Event()
    def opener(*a, **k):
        calls.append(1); gate.wait(1); return Response()
    def work():
        try: results.append(gm.observe('many-coalesced-regression', opener=opener))
        except Exception as exc: errors.append(exc)
    threads = [threading.Thread(target=work) for _ in range(6)]
    for thread in threads: thread.start()
    time.sleep(.05); gate.set()
    for thread in threads: thread.join()
    assert not errors and len(calls) == 1 and len(results) == 6


def test_primary_reset_and_http_date_backoff_are_not_silently_shortened(monkeypatch):
    from email.utils import formatdate
    monkeypatch.setattr(gm.time, 'time', lambda: 1000)
    waits = []
    assert gm._backoff({'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1300'}, waits.append) == 300
    assert gm._backoff({'Retry-After': formatdate(1120, usegmt=True)}, waits.append) == 120
    assert waits == [300, 120]
    with pytest.raises(gm.QuotaError, match='retry_after_exceeds_local_wait_bound') as exc:
        gm._backoff({'Retry-After': '7200'}, waits.append)
    assert exc.value.retry_after == 7200 and waits == [300, 120]


def test_changing_declared_class_cannot_bypass_observed_credential_cooldown():
    def limited(*args, **kwargs):
        raise urllib.error.HTTPError(gm.API_URL, 429, 'private', {'Retry-After': '7'}, None)
    with pytest.raises(gm.QuotaError):
        gm.observe('cross-class-cooldown', token_class='user_token', opener=limited, sleeper=lambda _: None)
    with pytest.raises(gm.QuotaError, match='rate_limit_cooldown'):
        gm.observe('cross-class-cooldown', token_class='app_installation',
                   opener=lambda *a, **k: pytest.fail('must not bypass cooldown'))
