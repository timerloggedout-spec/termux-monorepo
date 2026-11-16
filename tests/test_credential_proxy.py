import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "credential_proxy"))
from swap_proxy import load_config, translate  # noqa: E402

CFG = {
    "handles": {
        "gh-route": {
            "credential_env": "TEST_CRED_GH",
            "credential_header": "Authorization",
            "credential_prefix": "Bearer ",
            "allowed_hosts": ["api.github.com"],
            "allowed_path_prefixes": ["/repos/"],
        }
    }
}
ENV = {"TEST_CRED_GH": "secret-value-for-test"}


def test_swap_on_allowed_request():
    d = translate(CFG, "gh-route", "GET", "api.github.com", "/repos/a/b",
                  {"User-Agent": "agent"}, environ=ENV)
    assert d.allowed and d.reason == "swapped"
    assert d.outbound_headers["Authorization"] == "Bearer secret-value-for-test"
    assert d.outbound_headers["User-Agent"] == "agent"


def test_credential_never_in_audit():
    d = translate(CFG, "gh-route", "GET", "api.github.com", "/repos/a/b",
                  {}, environ=ENV)
    assert "secret-value-for-test" not in json.dumps(d.audit)


def test_unknown_handle_denied():
    d = translate(CFG, "nope", "GET", "api.github.com", "/repos/a/b", {}, environ=ENV)
    assert not d.allowed and d.reason == "unknown_handle"


def test_host_not_allowed():
    d = translate(CFG, "gh-route", "GET", "evil.example", "/repos/a/b", {}, environ=ENV)
    assert not d.allowed and d.reason == "host_not_allowed"


def test_path_not_allowed():
    d = translate(CFG, "gh-route", "GET", "api.github.com", "/user", {}, environ=ENV)
    assert not d.allowed and d.reason == "path_not_allowed"


def test_agent_supplied_authorization_refused():
    d = translate(CFG, "gh-route", "GET", "api.github.com", "/repos/a/b",
                  {"Authorization": "Bearer abcdefghijklmnopqrstuvwxyz"}, environ=ENV)
    assert not d.allowed and d.reason.startswith("agent_supplied_credential_header")


def test_credential_shaped_body_refused():
    d = translate(CFG, "gh-route", "POST", "api.github.com", "/repos/a/b",
                  {}, body_sample="key is ghp_abcdefghijklmnopqrstuvwxyz0123456789",
                  environ=ENV)
    assert not d.allowed and d.reason == "credential_shaped_input"


def test_unprovisioned_fails_closed_and_names_only():
    d = translate(CFG, "gh-route", "GET", "api.github.com", "/repos/a/b",
                  {}, environ={})
    assert not d.allowed
    assert d.reason == "credential_unprovisioned:TEST_CRED_GH"


def test_config_with_credential_value_rejected(tmp_path):
    bad = {"handles": {"h": {
        "credential_env": "E",
        "credential_header": "Authorization",
        "allowed_hosts": ["api.github.com"],
        "note": "ghp_abcdefghijklmnopqrstuvwxyz0123456789",
    }}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(bad))
    try:
        load_config(str(p))
    except ValueError as e:
        assert "credential-shaped" in str(e)
    else:
        raise AssertionError("config carrying a credential value must be rejected")
