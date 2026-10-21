"""Documented bearer model-list catalogs; public listing never grants admission."""
from __future__ import annotations

import math

ENDPOINTS = {
    "unorouter": "https://api.unorouter.com/v1/models",
    "routeway": "https://api.routeway.ai/v1/models",
    "requesty": "https://router.requesty.ai/v1/models",
    "xkiro": "https://api.xkiro.com/v1/models",
    "sealion": "https://api.sea-lion.ai/v1/models",
}
SECRETS = {provider: f"{provider.upper()}_API_KEY" for provider in ENDPOINTS}
# Official docs explicitly allow anonymous model discovery for these gateways.
PUBLIC_CATALOGS = frozenset({"routeway", "requesty", "xkiro"})
SOURCES = {
    "unorouter": "https://unorouter.com/en/docs/integrations/open-webui",
    "routeway": "https://docs.routeway.ai/getting-started/models",
    "requesty": "https://docs.requesty.ai/api-reference/endpoint/models-list",
    "xkiro": "https://docs.xkiro.com/models/tiers/",
    "sealion": "https://docs.sea-lion.ai/guides/inferencing/api",
}


def _rate(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except (OverflowError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _pricing(item, provider):
    pricing = item.get("pricing")
    if provider == "requesty":
        # The official wire schema is an ARRAY, not {tiers:[...]}. Thresholds
        # can make a later tier paid; use every tier, never only the first.
        if not isinstance(pricing, list) or not pricing:
            return {}, "unknown"
        parsed, all_rates = [], []
        for tier in pricing:
            if not isinstance(tier, dict):
                return {}, "unknown"
            threshold = tier.get("prompt_tokens_threshold")
            if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
                return {}, "unknown"
            inp, out = _rate(tier.get("input_price")), _rate(tier.get("output_price"))
            rates = [_rate(value) for key, value in tier.items() if key.endswith("_price")]
            if inp is None or out is None or any(rate is None for rate in rates):
                return {}, "unknown"
            parsed.append((inp, out))
            all_rates.extend(rates)
        if pricing[0]["prompt_tokens_threshold"] != 0:
            return {}, "unknown"
        thresholds = [tier["prompt_tokens_threshold"] for tier in pricing]
        if thresholds != sorted(set(thresholds)):
            return {}, "unknown"
        # Legacy price fields may coexist. A disagreement is unknown, not free.
        for key, index in (("input_price", 0), ("output_price", 1)):
            if key in item and _rate(item[key]) != parsed[0][index]:
                return {}, "unknown"
        return {"prompt": max(p[0] for p in parsed), "completion": max(p[1] for p in parsed)}, (
            "free_zero_price" if all(rate == 0 for rate in all_rates) else "paid"
        )
    if not isinstance(pricing, dict):
        return {}, "unknown"
    if provider == "routeway":
        def per_token(side):
            section = pricing.get(side)
            if not isinstance(section, dict) or section.get("unit") != "1M tokens":
                return None
            rate = _rate(section.get("price_per_million_t"))
            return rate / 1_000_000 if rate is not None else None
        inp, out = per_token("input"), per_token("output")
        # An underflowing nonzero price must never be relabeled free.
        zero = all(isinstance(pricing.get(side), dict) and pricing[side].get("price_per_million_t") == 0 for side in ("input", "output"))
        def extra_rates(node):
            if not isinstance(node, dict):
                return []
            result = []
            for key, value in node.items():
                if key == "price_per_million_t":
                    result.append(_rate(value))
                elif isinstance(value, dict):
                    result.extend(extra_rates(value))
            return result
        rates = extra_rates(pricing)
        if any(rate is None for rate in rates):
            return {}, "unknown"
        zero = zero and all(rate == 0 for rate in rates)
        if inp is not None and out is not None:
            return {"prompt": inp, "completion": out}, "free_zero_price" if zero else "paid"
        return {}, "unknown"
    # No schema-derived free status from an ID suffix or xKiro access_tier.
    inp, out = _rate(pricing.get("prompt")), _rate(pricing.get("completion"))
    rates = [_rate(value) for value in pricing.values()]
    if inp is None or out is None or any(rate is None for rate in rates):
        return {}, "unknown"
    return {"prompt": inp, "completion": out}, "free_zero_price" if all(rate == 0 for rate in rates) else "paid"


def poll(provider, token, get_json):
    payload, headers = get_json(ENDPOINTS[provider], token)
    items = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("invalid_response_shape")
    rows, seen = [], set()
    for item in items:
        model_id = item.get("id")
        if not isinstance(model_id, str) or not model_id.strip() or any(ord(c) < 32 or ord(c) == 127 for c in model_id):
            raise ValueError("invalid_model")
        if model_id in seen:
            continue
        seen.add(model_id)
        pricing, price_class = _pricing(item, provider)
        row = {
            "provider": provider, "id": model_id,
            "name": item.get("name") if isinstance(item.get("name"), str) else model_id,
            "pricing": pricing, "pricing_classification": price_class,
            "access_classification": "catalog_pricing_only", "access_source": None,
            "access_source_observed": None, "cadence": "catalog",
            "free_suffix": model_id.endswith(":free"), "context_length": None,
            "max_output_tokens": None, "raw_source": f"{provider}:/v1/models",
        }
        for source, dest in (("context_length", "context_length"), ("context_window", "context_length"), ("max_output_tokens", "max_output_tokens")):
            value = item.get(source)
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                row[dest] = value
        if provider == "routeway":
            row["active"] = item.get("available") if isinstance(item.get("available"), bool) else None
            caps = item.get("capabilities")
            row["capabilities"] = {key: value for key, value in caps.items() if isinstance(value, bool)} if isinstance(caps, dict) else None
        if provider == "xkiro":
            row["account_free_tier_candidate"] = item.get("access_tier") == "free"
            row["quota_status"] = "unknown"
        rows.append(row)
    return rows, headers
