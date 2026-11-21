#!/usr/bin/env python3
"""
CI mode for multi-ai-cli – non-interactive DeepSeek review path.

Implements: RL-18
Security:
- Never persist cookies / tokens / PoW answers across jobs.
- Cache dir is RUNNER_TEMP only; caller must scrub.
- OPERATOR / DEEPSEEK_TOKEN from env only; never cross-wire.
- Artifact JSON is metadata-only (no model body).
"""
from __future__ import annotations

import argparse
import json
import os
import re
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


LIVE3_MARKER = "live-3-phrases-deepseek dispatch"
_LIVE3_STAMP_RE = re.compile(
    r"dispatch #(\d+) \u00b7 cell `([^`]+)`.*?"
    r"prompt sha256 `([0-9a-f]+)`.*?instance `([^`]*)`", re.S)


def _live3_dispatch(event: dict) -> dict | None:
    """Opt-in live-3 dispatch detection (doe-expert ruling (i-a)).

    A PR issue_comment carrying the live-3 stamp header is a
    designed dispatch: the comment body (minus the one-line stamp
    envelope) IS the composed prompt, administered verbatim. Any
    other event/comment returns None and the surface behaves
    exactly as before — no behavior change for non-dispatch
    traffic.
    """
    if event.get("action") != "created":
        return None
    comment = event.get("comment") or {}
    # Only repository-trusted authors may administer a dispatch:
    # the marker alone must never let an arbitrary commenter drive
    # the bot's prompt (review finding, PR #2856).
    if comment.get("author_association") not in (
            "OWNER", "MEMBER", "COLLABORATOR"):
        return None
    body = comment.get("body") or ""
    if LIVE3_MARKER not in body:
        return None
    issue = event.get("issue") or {}
    if not issue.get("pull_request") or not issue.get("number"):
        return None
    prompt = body
    if body.lstrip().startswith("[MUSEai]") and "\n\n" in body:
        prompt = body.split("\n\n", 1)[1]
    m = _LIVE3_STAMP_RE.search(body)
    stamp = ({"dispatch_no": int(m.group(1)), "cell": m.group(2),
              "prompt_sha256_12": m.group(3),
              "instance_12": m.group(4)} if m else {})
    return {"pr": int(issue["number"]), "prompt": prompt,
            "stamp": stamp}


def run_ci(
    event: dict,
    workspace: str,
    operator_token: str | None = None,
    pr_override: str | None = None,
) -> dict:
    workspace_path = Path(workspace)
    _configure_pow(workspace_path)

    gh_env = _gh_env(operator_token)
    pr_number = pr_override or event.get("pull_request", {}).get("number")
    dispatch = _live3_dispatch(event)
    if dispatch is not None and pr_number is None:
        pr_number = dispatch["pr"]
    if pr_number is not None:
        pr_number = str(pr_number)
    repo = (
        event.get("repository", {}).get("full_name")
        or os.environ.get("GITHUB_REPOSITORY")
    )
    action = event.get("action")
    decisions: list[dict] = []
    status = "ok"

    if not pr_number or not repo:
        return {
            "actions": [],
            "event": action,
            "pr": pr_number,
            "provider_used": "deepseek",
            "status": "skipped",
            "skipped": "missing pr or repo",
        }

    if not os.environ.get("DEEPSEEK_TOKEN"):
        print("::error::DEEPSEEK_TOKEN unset — model auth required", file=sys.stderr)
        return {
            "actions": [{"type": "error", "message": "DEEPSEEK_TOKEN unset"}],
            "event": action,
            "pr": pr_number,
            "provider_used": "deepseek",
            "status": "error",
        }

    if dispatch is not None:
        diff = ""
    try:
        if dispatch is None:
            diff = subprocess.check_output(
                ["gh", "pr", "diff", str(pr_number), "--repo", repo],
                env=gh_env,
                text=True,
                timeout=60,
            )
    except Exception as e:
        print(f"::error::diff retrieval failed: {e}", file=sys.stderr)
        return {
            "actions": [{"type": "error", "message": "diff_retrieval_failed"}],
            "event": action,
            "pr": pr_number,
            "provider_used": "deepseek",
            "status": "error",
        }

    if dispatch is None and not diff.strip():
        return {
            "actions": [],
            "event": action,
            "pr": pr_number,
            "provider_used": "deepseek",
            "status": "skipped",
            "skipped": "empty_diff",
        }

    try:
        mgr = SessionManager()
        backend = DeepSeekBackend(mgr)
        if dispatch is not None:
            prompt = dispatch["prompt"]
        else:
            prompt = (
                "You are a code reviewer for a Termux monorepo. "
                "Focus on security, correctness, and CI reliability. "
                "Be concise. Flag Class 3/4 secret risks. "
                "Never echo tokens, cookies, or secrets from the "
                "diff.\n\n"
                f"PR #{pr_number} diff (truncated):\n\n{diff[:8000]}"
            )
        analysis = backend.send_message(prompt, [])

        if (
            analysis
            and not str(analysis).startswith("Error:")
            and not str(analysis).startswith("[No content returned]")
        ):
            body = str(analysis)
            if len(body) > 4000:
                body = body[:4000] + "\n\n_(truncated)_"
            if dispatch is not None:
                st = dispatch["stamp"]
                signature = (
                    "\n\n---\n*DeepSeek CI (deepcli) · live-3 "
                    f"dispatch #{st.get('dispatch_no', '?')} · cell "
                    f"{st.get('cell', '?')} · prompt sha256 "
                    f"{st.get('prompt_sha256_12', '?')}*"
                )
            else:
                signature = (
                    "\n\n---\n*DeepSeek CI (multi-ai-cli / deepcli "
                    "PoW) · "
                    "ephemeral session · Implements: RL-18 · Fixes #109*"
                )
            comment_body = body + signature
            posted = False
            try:
                res = subprocess.run(
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
                posted = res.returncode == 0
            except Exception as e:
                print(f"::warning::Failed to post PR comment: {e}", file=sys.stderr)

            if dispatch is not None:
                decisions.append(
                    {
                        "type": "live3_dispatch",
                        "pr": pr_number,
                        "posted": posted,
                        "chars": len(comment_body),
                        "dispatch_no": dispatch["stamp"].get(
                            "dispatch_no"),
                        "cell": dispatch["stamp"].get("cell"),
                    }
                )
            else:
                decisions.append(
                    {
                        "type": "pr_review",
                        "pr": pr_number,
                        "posted": posted,
                        "chars": len(comment_body),
                    }
                )
        else:
            print("::warning::empty or invalid DeepSeek analysis", file=sys.stderr)
            status = "error"
            decisions.append({"type": "error", "message": "empty_analysis"})
    except Exception as e:
        print(f"::error::DeepSeek analysis failed: {type(e).__name__}", file=sys.stderr)
        status = "error"
        decisions.append({"type": "error", "message": type(e).__name__})

    if any(d.get("type") == "error" for d in decisions):
        status = "error"

    return {
        "actions": decisions,
        "event": action,
        "pr": pr_number,
        "provider_used": "deepseek",
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--cache-dir", default="/tmp/deepseek-cache")
    parser.add_argument("--pr", default="", help="PR number override")
    args = parser.parse_args()

    # Isolate any incidental HOME-relative writes
    os.environ.setdefault("MULTI_AI_CACHE_DIR", args.cache_dir)
    os.makedirs(args.cache_dir, exist_ok=True)
    cache_path = Path(args.cache_dir)
    if not cache_path.is_symlink():
        try:
            os.chmod(args.cache_dir, 0o700)
        except Exception:
            pass

    event = _load_event()
    result = run_ci(
        event=event,
        workspace=args.workspace,
        operator_token=os.environ.get("OPERATOR")
        or os.environ.get("GH_TOKEN"),
        pr_override=args.pr or None,
    )

    # Metadata only — never store model body (secret echo risk)
    safe = {
        "status": result.get("status"),
        "event": result.get("event"),
        "pr": result.get("pr"),
        "provider_used": result.get("provider_used"),
        "actions": [
            {k: v for k, v in a.items() if k != "summary"}
            for a in result.get("actions", [])
        ],
        "skipped": result.get("skipped"),
    }

    output_path = Path("deepseek_output.json")
    if output_path.is_symlink():
        raise ValueError(f"Output path {output_path} cannot be a symlink")

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = 0o600
    try:
        fd = os.open(output_path, flags, mode)
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(safe, f, indent=2)
    except Exception:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(safe, f, indent=2)
    if not output_path.is_symlink():
        try:
            os.chmod(output_path, 0o600)
        except Exception:
            pass

    print(
        f"CI run completed. status={safe.get('status')} "
        f"actions={[a.get('type') for a in safe.get('actions', [])]}"
    )

    if safe.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
