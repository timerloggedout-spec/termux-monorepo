"""Shared endpoint admission for retired hosting providers."""

from urllib.parse import urlparse

RETIRED_HOSTS = frozenset({"api.fly.io", "app.koyeb.com"})
RETIRED_SUFFIXES = (".fly.dev", ".koyeb.app")


def retired_hindsight_endpoint_reason(base_url: str | None) -> str | None:
    """Return a lifecycle block reason for a retired Fly/Koyeb endpoint."""
    if not base_url:
        return None
    candidate = base_url if "://" in base_url else f"https://{base_url}"
    host = (urlparse(candidate).hostname or "").lower().rstrip(".")
    if host in RETIRED_HOSTS or any(host.endswith(suffix) for suffix in RETIRED_SUFFIXES):
        return f"HINDSIGHT_BASE_URL targets retired provider host: {host}"
    return None
