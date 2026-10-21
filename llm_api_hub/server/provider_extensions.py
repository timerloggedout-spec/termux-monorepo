"""Reviewed metadata for explicitly admitted operational provider extensions.

Endpoints are fixed reviewed URLs, never configurable per request. Entries do not
grant admission; exact-model free/public/terms/expiry checks remain elsewhere.
"""
ENDPOINTS = {
    "typhoon": ("https://api.opentyphoon.ai/v1/chat/completions", ("OPENTYPHOON_API_KEY", "TYPHOON_API_KEY")),
    "unorouter": ("https://api.unorouter.com/v1/chat/completions", ("UNOROUTER_API_KEY",)),
    "routeway": ("https://api.routeway.ai/v1/chat/completions", ("ROUTEWAY_API_KEY",)),
    "requesty": ("https://router.requesty.ai/v1/chat/completions", ("REQUESTY_API_KEY",)),
    "xkiro": ("https://api.xkiro.com/v1/chat/completions", ("XKIRO_API_KEY",)),
    "xfyun": ("https://spark-api-open.xf-yun.com/v1/chat/completions", ("XFYUN_API_KEY", "IFLYTEK_SPARK_API_PASSWORD")),
    "sealion": ("https://api.sea-lion.ai/v1/chat/completions", ("SEALION_API_KEY",)),
}
CATALOG_ENDPOINTS = {
    "unorouter": "https://api.unorouter.com/v1/models",
    "routeway": "https://api.routeway.ai/v1/models",
    "requesty": "https://router.requesty.ai/v1/models",
    "xkiro": "https://api.xkiro.com/v1/models",
    "sealion": "https://api.sea-lion.ai/v1/models",
}
SOURCES = {
    "typhoon": ("https://docs.opentyphoon.ai/en/api-reference/", "https://opentyphoon.ai/tac"),
    "unorouter": ("https://unorouter.com/en", "https://unorouter.com/en/docs/integrations/open-webui"),
    "routeway": ("https://docs.routeway.ai/getting-started/introduction", "https://docs.routeway.ai/getting-started/models"),
    "requesty": ("https://docs.requesty.ai/quickstart", "https://docs.requesty.ai/features/free-models"),
    "xkiro": ("https://docs.xkiro.com/", "https://docs.xkiro.com/guides/authentication/"),
    "xfyun": ("https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html",),
    "sealion": ("https://docs.sea-lion.ai/guides/inferencing/api",),
}
SETUP_CAVEATS = {
    "typhoon": "Use an independently authorized account/key; documented light research usage is free but quota entitlement is not guaranteed.",
    "unorouter": "Requires signup and an independently obtained key; exact :free model suffix is required and does not establish quota entitlement.",
    "routeway": "Use only the exact :free model path; the free suffix is mandatory.",
    "requesty": "Use only exact currently confirmed free model IDs; do not use policy/ or bare routing aliases.",
    "xkiro": "Verify account plan and current free quota before use.",
    "xfyun": "Only exact lite model is treated as confirmed free; credential alias may be account-specific.",
    "sealion": "API key may be trial-based; no permanent free entitlement is guaranteed.",
}
