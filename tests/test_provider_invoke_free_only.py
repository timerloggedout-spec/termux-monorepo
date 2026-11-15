"""No-cost provider model selection contract for QUE inference dispatch."""

from scripts.ops import provider_invoke as invoke


def row(model_id, **overrides):
    value = {
        "id": model_id,
        "pricing_classification": "unknown",
        "access_classification": "catalog_pricing_only",
        "entitlement_verification": "unknown",
        "free_suffix": False,
    }
    value.update(overrides)
    return value


def test_selects_zero_price_chat_model_without_requiring_provider_quota_counter():
    candidate = row(
        "daily-pool/free-chat",
        pricing_classification="free_zero_price",
        quota_class="daily_pool_no_provider_quota",
        pool_status="available",
    )
    assert invoke.select_free_chat_model([candidate]) == "daily-pool/free-chat"


def test_selects_openrouter_free_suffix_model():
    candidate = row("vendor/model:free", free_suffix=True)
    assert invoke.select_free_chat_model([candidate]) == "vendor/model:free"


def test_selects_free_trial_only_when_entitlement_is_verified():
    unverified = row(
        "trial/unverified",
        access_classification="free_trial",
        entitlement_verification="unknown",
    )
    verified = row(
        "trial/verified",
        access_classification="free_trial",
        entitlement_verification="verified",
    )
    assert invoke.select_free_chat_model([unverified, verified]) == "trial/verified"


def test_rejects_paid_unknown_and_non_chat_models():
    candidates = [
        row("paid/model", pricing_classification="paid"),
        row("unknown/model"),
        row("free/embed-model", pricing_classification="free_zero_price"),
        row("free/tts-model", free_suffix=True),
    ]
    assert invoke.select_free_chat_model(candidates) is None


def test_explicit_model_must_match_an_exact_verified_no_cost_chat_model():
    candidates = [
        row("free/model", pricing_classification="free_zero_price"),
        row("paid/model", pricing_classification="paid"),
    ]
    assert invoke.select_free_chat_model(candidates, "free/model") == "free/model"
    assert invoke.select_free_chat_model(candidates, "paid/model") is None
    assert invoke.select_free_chat_model(candidates, "free/mod") is None
