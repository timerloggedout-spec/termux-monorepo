#!/usr/bin/env python3
"""
CI mode for multi-ai-cli – non-interactive DeepSeek review path.

Security:
- Never persist cookies / tokens / PoW answers across jobs.
- Cache dir is RUNNER_TEMP only; caller must scrub.
- OPERATOR / DEEPSEEK_TOKEN from env only.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import backends.deepseek as ds_mod
from backends.deepseek import DeepSeekBackend
from core.session_manager import SessionManager


def _configure_pow(workspace: Path) -> None:
    solver = os.environ.get("DEEPSEEK_WASM_SOLVER")
    if solver:
        ds_mod.WASM_SOLVER = Path(solver)
    else:
        candidate = workspace / "deepcli" / "pow_solver.js"
        if candidate.is_file():
            ds_mod.WASM_SOLVER = candidate


def _load_event() -> dict:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: event load failed: {e}", file=sys.stderr)
    return {}


def _gh_env(token: str | None) -> dict:
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
    return env


def run_ci(
    event: dict,
    workspace: str,
    operator_token: str | None,
    pr_override: str | None = None,
) -> dict:
    workspace_path = Path(workspace)
    _configure_pow(workspace_path)

    gh_env = _gh_env(operator_token)
    pr_number = pr_override or event.get("pull_request", {}).get("number")
    if pr_number is not None:
        pr_number = str(pr_number)
    repo = (
        event.get("repository", {}).get("full_name")
        or os.environ.get("GITHUB_REPOSITORY")
    )
    action = event.get("action")
    decisions: list[dict] = []

    if not pr_number or not repo:
        return {
            "actions": [],
            "event": action,
            "pr": pr_number,
            "provider_used": "deepseek",
            "skipped": "missing pr or repo",
        }

    # Prefer DEEPSEEK_TOKEN; never fall back to GH operator token as model auth
    if not os.environ.get("DEEPSEEK_TOKEN"):
        print(
            "Warning: DEEPSEEK_TOKEN unset — DeepSeek backend may fail",
            file=sys.stderr,
        )

    diff = ""
    try:
        diff = subprocess.check_output(
            ["gh", "pr", "diff", str(pr_number), "--repo", repo],
            env=gh_env,
            text=True,
            timeout=60,
        )
    except Exception as e:
        diff = f"Could not retrieve diff: {e}"

    try:
        mgr = SessionManager()
        backend = DeepSeekBackend(mgr)
        prompt = (
            "You are a code reviewer for a Termux monorepo. "
            "Focus on security, correctness, and CI reliability. "
            "Be concise. Flag Class 3/4 secret risks.\n\n"
            f"PR #{pr_number} diff (truncated):\n\n{diff[:8000]}"
        )
        analysis = backend.send_message(prompt, [])

        if (
            analysis
            and not str(analysis).startswith("Error:")
            and not str(analysis).startswith("[No content returned]")
        ):
            signature = (
                "\n\n---\n*DeepSeek CI (multi-ai-cli / deepcli PoW) · "
                "ephemeral session · Fixes #109*"
            )
            comment_body = (str(analysis)[:1900] + signature)
            try:
                subprocess.run(
                    [
                        "gh",
                        "pr",
                        "comment",
                        str(pr_number),
                        "--body",
                        comment_body,
                        "--repo",
                        repo,
                    ],
                    env=gh_env,
                    check=False,
                    timeout=30,
                )
            except Exception as e:
                print(f"Failed to post PR comment: {e}", file=sys.stderr)

            decisions.append(
                {
                    "type": "pr_review",
                    "pr": pr_number,
                    "summary": comment_body[:200],
                }
            )
        else:
            print(
                f"Warning: empty/invalid DeepSeek analysis: {analysis!r}",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"Error during DeepSeek analysis: {e}", file=sys.stderr)
        decisions.append({"type": "error", "message": str(e)[:300]})

    return {
        "actions": decisions,
        "event": action,
        "pr": pr_number,
        "provider_used": "deepseek",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--cache-dir", default="/tmp/deepseek-cache")
    parser.add_argument("--pr", default="", help="PR number override")
    args = parser.parse_args()

    os.makedirs(args.cache_dir, exist_ok=True)
    try:
        os.chmod(args.cache_dir, 0o700)
    except Exception:
        pass

    event = _load_event()
    result = run_ci(
        event=event,
        workspace=args.workspace,
        operator_token=os.environ.get("OPERATOR_TOKEN")
        or os.environ.get("GH_TOKEN"),
        pr_override=args.pr or None,
    )

    output_path = Path("deepseek_output.json")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = 0o600
    try:
        fd = os.open(output_path, flags, mode)
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    try:
        os.chmod(output_path, 0o600)
    except Exception:
        pass

    print(f"CI run completed. Decisions: {result.get('actions', [])}")


if __name__ == "__main__":
    main()
