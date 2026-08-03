#!/usr/bin/env python3
"""
Sentry SDK bootstrap for termux-monorepo / ArchWiz.

Import and call init_sentry() as early as possible in any long-running process
(dashboard, dispatch pipeline, deepcli, autonomous runner, aiohttp apps, etc.).

Multiple Sentry projects are provisioned under the same org:
  - python   — default CLI / ArchWiz / deepcli
  - aiohttp  — aiohttp web services

Override with SENTRY_DSN or SENTRY_PROJECT=python|aiohttp.
Browser (JS) and Rust use separate SDKs — see docs/SENTRY_LINEAR.md.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

# Official project DSNs from Sentry GitHub integration
DSN_PYTHON = (
    "https://a922fa6cd019e401e779d420d28b155c@o4511844213522432.ingest.us.sentry.io/4511844223680512"
)
DSN_AIOHTTP = (
    "https://c7fb0bb5cf4210fae90119131c12b320@o4511844213522432.ingest.us.sentry.io/4511844256055296"
)

PROJECT_DSNS = {
    "python": DSN_PYTHON,
    "aiohttp": DSN_AIOHTTP,
}

DEFAULT_DSN = DSN_PYTHON
_initialized = False


def _resolve_dsn(dsn: Optional[str] = None, project: Optional[str] = None) -> Optional[str]:
    if dsn:
        return dsn
    env_dsn = os.environ.get("SENTRY_DSN")
    if env_dsn:
        return env_dsn
    proj = (project or os.environ.get("SENTRY_PROJECT") or "python").strip().lower()
    return PROJECT_DSNS.get(proj, DEFAULT_DSN)


def init_sentry(
    dsn: Optional[str] = None,
    *,
    project: Optional[str] = None,
    traces_sample_rate: float = 1.0,
    profile_session_sample_rate: float = 1.0,
    profile_lifecycle: str = "trace",
    enable_logs: bool = True,
    send_default_pii: bool = True,
) -> bool:
    """Initialize Sentry SDK. Idempotent. Returns True if active.

    project: "python" (default) or "aiohttp" — selects the matching DSN
    when SENTRY_DSN is not set.
    """
    global _initialized
    if _initialized:
        return True

    resolved = _resolve_dsn(dsn, project)
    if not resolved:
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        print(
            "[sentry] sentry-sdk not installed. Run: pip install 'sentry-sdk'",
            file=sys.stderr,
        )
        return False

    logging_integration = LoggingIntegration(
        level=None,  # capture all levels as breadcrumbs
        event_level=None,  # do not auto-send log records as events
    )

    # AIOHTTPIntegration is auto-enabled when aiohttp is importable
    sentry_sdk.init(
        dsn=resolved,
        send_default_pii=send_default_pii,
        enable_logs=enable_logs,
        traces_sample_rate=traces_sample_rate,
        profile_session_sample_rate=profile_session_sample_rate,
        profile_lifecycle=profile_lifecycle,
        integrations=[logging_integration],
        environment=os.environ.get("ARCHWIZ_ENV", "local"),
        release=os.environ.get("SENTRY_RELEASE"),
    )
    _initialized = True
    return True


def capture_exception(exc: BaseException) -> None:
    if not _initialized:
        init_sentry()
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)
    except Exception:
        pass


def capture_message(msg: str, level: str = "info") -> None:
    if not _initialized:
        init_sentry()
    try:
        import sentry_sdk
        sentry_sdk.capture_message(msg, level=level)
    except Exception:
        pass


def start_profiler() -> None:
    if not _initialized:
        init_sentry()
    try:
        import sentry_sdk
        sentry_sdk.profiler.start_profiler()
    except Exception:
        pass


def stop_profiler() -> None:
    try:
        import sentry_sdk
        sentry_sdk.profiler.stop_profiler()
    except Exception:
        pass


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else "python"
    ok = init_sentry(project=proj)
    print(f"Sentry initialized ({proj}): {ok}")
    if ok:
        capture_message(f"termux-monorepo sentry_init self-test [{proj}]", level="info")
        print("Test message sent. Check Sentry dashboard.")
