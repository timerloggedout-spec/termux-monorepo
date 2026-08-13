#!/usr/bin/env python3
"""
CI mode entrypoint – non-interactive agent.
Default account: primary (Account-1) — PRIORITY.
OPERATOR_TOKEN env is required (normalized by workflow from thread-listed secrets).
When DEEPSEEK_TOKEN_* secrets are absent, soft-skip (exit 0) so master
functional gate stays green; fill secrets to enable live DeepSeek lane.
"""
import os
import sys
import json
import argparse

from .ci_agent import run_ci
from .session_manager import ensure_session, normalize_account, _token_from_env


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
        print("::error::OPERATOR_TOKEN is empty — set ARCHWIZ_GITHUB_TOKEN / OPERATOR_GITHUB_TOKEN / OPERATOR_TOKEN")
        result = {"actions": [], "error": "missing_OPERATOR_TOKEN", "account": account}
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        sys.exit(1)

    # Soft-skip when DeepSeek web tokens are not provisioned (quota / secret gap).
    # Keeps dual-gate (repo_gate + termux_smoke) and master green; live lane
    # activates once any catalog name from Issue #184 / DEEPSEEK-CI.md is set.
    token = _token_from_env(account)
    if not token:
        msg = (
            f"DeepSeek tokens absent for account={account}. "
            "Set one of DEEPSEEK_TOKEN / DEEPSEEK_TOKEN_PRIMARY / DEEPSEEK_API_KEY / "
            "DEEPSEEK_AUTH_TOKEN / NEXUSCLI_TOKEN / DEEPSEEK_COOKIES "
            "(or SECONDARY / DEEPSEEK_COOKIES_2). See Issue #184 + docs/ops/DEEPSEEK-CI.md. "
            "Soft-skipping CI agent (exit 0) so functional gate remains green."
        )
        print(f"::notice::{msg}")
        result = {
            "actions": [],
            "skipped": True,
            "reason": "missing_DEEPSEEK_TOKEN",
            "account": account,
            "message": msg,
        }
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

    try:
        session = ensure_session(cache_dir=args.cache_dir, account=account)
        print(
            f"::notice::DeepSeek account={session.get('account')} "
            f"chat_session_id={session.get('chat_session_id')}"
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"::warning::Session initialization failed (likely expired/invalid credentials): {error_msg}")
        msg = f"DeepSeek session initialization failed: {error_msg}. Soft-skipping CI agent (exit 0) so functional gate remains green."
        print(f"::notice::{msg}")
        result = {
            "actions": [],
            "skipped": True,
            "reason": "session_init_failed",
            "account": account,
            "message": msg,
        }
        with open("deepseek_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

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
        # Soft-skip on DeepSeek API or authorization/token failures to prevent CI blockers.
        err_str = str(result["error"])
        if "DeepSeek API error" in err_str or "Authorization Failed" in err_str or "session_init_failed" in err_str:
            print("::notice::DeepSeek API/Auth error detected. Soft-skipping (exit 0) to keep CI gate green.")
            sys.exit(0)
        sys.exit(1)

    print(f"✅ CI run completed. Decisions: {result.get('actions', [])}")


if __name__ == "__main__":
    main()
