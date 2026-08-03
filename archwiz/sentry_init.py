#!/usr/bin/env python3
"""
Sentry SDK bootstrap for termux-monorepo / ArchWiz.

Import and call init_sentry() as early as possible in any long-running process
(dashboard, dispatch pipeline, deepcli, autonomous runner, etc.).

DSN is the one provisioned via GitHub Sentry integration.
Override with SENTRY_DSN env var if needed (e.g. staging vs production).
"""
from __future__ import annotations

import os
import sys
from typing import Optional

# Official project DSN from Sentry GitHub integration
DEFAULT_DSN = (
    "https://a922fa6cd019e401e779d420d28b155c@o4511844213522432.ingest.us.sentry.io/4511844223680512"
)

_initialized = False


def init_sentry(
    dsn: Optional[str] = None,
    *,
    traces_sample_rate: float = 1.0,
    profile_session_sample_rate: float = 1.0,
    enable_logs: bool = True,
    send_default_pii: bool = True,
) -> bool:
    """Initialize Sentry SDK. Idempotent. Returns True if active."""
    global _initialized
    if _initialized:
        return True

    dsn = dsn or os.environ.get("SENTRY_DSN") or DEFAULT_DSN
    if not dsn:
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

    sentry_sdk.init(
        dsn=dsn,
        send_default_pii=send_default_pii,
        enable_logs=enable_logs,
        traces_sample_rate=traces_sample_rate,
        profile_session_sample_rate=profile_session_sample_rate,
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
    ok = init_sentry()
    print(f"Sentry initialized: {ok}")
    if ok:
        # Verify by sending a test message (visible in Sentry Issues / Logs)
        capture_message("termux-monorepo sentry_init self-test", level="info")
        print("Test message sent. Check Sentry dashboard.")
