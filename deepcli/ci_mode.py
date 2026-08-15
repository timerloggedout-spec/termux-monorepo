#!/usr/bin/env python3
"""
CI mode entrypoint – non-interactive agent.
Default account: primary (Account-1) — PRIORITY.
OPERATOR_TOKEN env is required (normalized by workflow from ARCHWIZ_GITHUB_TOKEN first).
Cookies and model auth secrets are expected to be present.
Hard-fail (exit 1) on missing credentials, session init failure, or API/auth errors.
No soft-skip fallbacks.
"""
import os
import sys
import json
import argparse

from .ci_agent import run_ci
from .session_manager import ensure_session, normalize_account, _token_from_env


def sanitize_error_msg(e: str | Exception) -> str:
    """
    Sanitize error message to prevent provider response body or credential-derived detail leakage
    into step summaries. Returns a generic, safe string.
    """
    err_str = str(e)
    if "40003" in err_str or "Authorization Failed" in err_str or "invalid token" in err_str:
        return "Authentication failure (invalid, expired, or revoked DeepSeek credentials)."
    if "401" in err_str or "403" in err_str:
        return "HTTP 401/403: DeepSeek web wrapper authorization declined."
    if "Connection" in err_str or "resolve" in err_str or "unreachable" in err_str:
        return "Network connection failure (unable to connect or resolve host)."
    if "timeout" in err_str or "timed out" in err_str:
        return "Network timeout occurred while communicating with DeepSeek."
    return "DeepSeek system/API error. Please check the workflow run logs for details."


def _write_step_summary(reason: str, details_or_exception: str | Exception) -> None:
    """
    Helper to safely populate GITHUB_STEP_SUMMARY with a sanitized error message.
    """
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    sanitized = sanitize_error_msg(details_or_exception)
    try:
        with open(summary_file, "a", encoding="utf-8") as sf:
            sf.write(
                f"\n### ❌ DeepSeek CI Failed\n"
                f"* **Reason:** {reason}\n"
                f"* **Details:** {sanitized}\n"
            )
    except Exception as gha_err:
        print(f"Warning: Failed to write GITHUB_STEP_SUMMARY: {gha_err}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument(
        "--account",
        default=os.environ.get("DEEPSEEK_ACCOUNT", "account-1"),
        help="DeepSeek webWrapper account: account-1/primary (default) or account-2/secondary",
    )
    args = parser.parse_args()

    os.environ["GITHUB_WORKSPACE"] = args.workspace
    account = normalize_account(args.account)

    operator_token = os.environ.get("OPERATOR_TOKEN") or ""
    if not operator_token:
        print("::error::OPERATOR_TOKEN is empty — set ARCHWIZ_GITHUB_TOKEN (preferred) / OPERATOR_GITHUB_TOKEN / OPERATOR_TOKEN")
        result = {"actions": [], "error": "missing_OPERATOR_TOKEN", "account": account}
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        sys.exit(1)

    # Hard-fail when DeepSeek web tokens/cookies are not provisioned.
    token = _token_from_env(account)
    if not token:
        msg = (
            f"DeepSeek tokens/cookies absent for account={account}. "
            "Set one of DEEPSEEK_TOKEN / DEEPSEEK_TOKEN_PRIMARY / DEEPSEEK_API_KEY / "
            "DEEPSEEK_AUTH_TOKEN / NEXUSCLI_TOKEN / DEEPSEEK_COOKIES "
            "(or SECONDARY / DEEPSEEK_COOKIES_2). See Issue #184 + docs/ops/DEEPSEEK-CI.md."
        )
        print(f"::error::{msg}")
        result = {
            "actions": [],
            "error": "missing_DEEPSEEK_TOKEN",
            "account": account,
            "message": msg,
        }
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        _write_step_summary("Missing DeepSeek credentials", msg)
        sys.exit(1)

    try:
        session = ensure_session(cache_dir=args.cache_dir, account=account)
        print(
            f"::notice::DeepSeek account={session.get('account')} "
            f"chat_session_id={session.get('chat_session_id')}"
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)[:200]}"
        msg = f"DeepSeek session initialization failed: {error_msg}"
        print(f"::error::{msg}")
        _write_step_summary("Session initialization failed", e)
        result = {
            "actions": [],
            "error": "session_init_failed",
            "account": account,
            "message": msg,
        }
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        sys.exit(1)

    try:
        event = json.loads(args.event)
    except json.JSONDecodeError as e:
        print(f"::warning::Invalid event JSON ({e}); using empty event")
        event = {}

    peer = {"provider": "deepseek", "account": account}

    result = run_ci(
        event=event,
        session=session,
        peer=peer,
        workspace=args.workspace,
        operator_token=operator_token,
    )
    result["account"] = account
    result["chat_session_id"] = session.get("chat_session_id")

    with open("deepseek_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if result.get("error"):
        print(f"::error::{result['error']}")
        _write_step_summary("API/runtime error", result["error"])
        sys.exit(1)

    print(f"✅ CI run completed. Decisions: {result.get('actions', [])}")


if __name__ == "__main__":
    main()
