#!/usr/bin/env python3
"""
CI mode for multi-ai-cli – runs the agent non-interactively using DeepSeek,
reading GitHub event payload, and outputting JSON securely.
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Use relative module paths inside multi-ai-cli
sys.path.insert(0, str(Path(__file__).parent))

from core.session_manager import SessionManager
import backends.deepseek as ds_mod
from backends.deepseek import DeepSeekBackend

def run_ci(event, workspace, operator_token):
    """
    Non-interactive agent loop using DeepSeek web-wrapper.
    """
    # Dynamically resolve WASM_SOLVER path in GHA
    ds_mod.WASM_SOLVER = Path(workspace) / "deepcli" / "pow_solver.js"

    # Set up GitHub CLI env with token
    gh_env = os.environ.copy()
    if operator_token:
        gh_env['GH_TOKEN'] = operator_token

    pr_number = event.get('pull_request', {}).get('number')
    repo = event.get('repository', {}).get('full_name') or os.environ.get('GITHUB_REPOSITORY')
    action = event.get('action')

    decisions = []

    if action in ['opened', 'synchronize', 'reopened'] and pr_number and repo:
        # Get PR diff
        diff_cmd = ['gh', 'pr', 'diff', str(pr_number), '--repo', repo]
        try:
            diff = subprocess.check_output(diff_cmd, env=gh_env, text=True)
        except Exception as e:
            diff = f"Could not retrieve diff: {e}"

        # Initialize the DeepSeek backend and perform code review
        try:
            # DeepSeek token can be loaded from env or config.yaml
            if not os.environ.get("DEEPSEEK_TOKEN"):
                os.environ["DEEPSEEK_TOKEN"] = operator_token or ""

            mgr = SessionManager()
            backend = DeepSeekBackend(mgr)

            prompt = f"You are a code reviewer. Analyze the diff and suggest improvements:\n\n{diff[:8000]}"
            analysis = backend.send_message(prompt, [])

            # Ensure we only post PR comment on successful analysis (skip error/mock strings)
            if analysis and not analysis.startswith("Error:") and not analysis.startswith("[No content returned]"):
                # Tracing signature metadata suffix
                signature = f"\n\n---\n*Bot Review powered by @deepseek-cli{{provider: deepseek, model: deepseek-reasoner}}*"
                comment_body = analysis[:1900] + signature

                # Comment on the PR
                comment_cmd = ['gh', 'pr', 'comment', str(pr_number), '--body', comment_body, '--repo', repo]
                try:
                    subprocess.run(comment_cmd, env=gh_env, check=False)
                except Exception as e:
                    print(f"Failed to post PR comment: {e}")

                decisions.append({
                    'type': 'pr_review',
                    'pr': pr_number,
                    'summary': comment_body[:200],
                })
            else:
                print(f"Warning: DeepSeek analysis returned empty or invalid review: {analysis}", file=sys.stderr)
        except Exception as e:
            print(f"Error during DeepSeek analysis: {e}", file=sys.stderr)

    return {
        'actions': decisions,
        'event': event.get('action'),
        'pr': pr_number,
        'provider_used': 'deepseek',
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, help='GitHub workspace path')
    parser.add_argument('--cache-dir', default='/tmp/deepseek-cache', help='Directory for session cache')
    args = parser.parse_args()

    # Enforce secure directory creation (0o700)
    os.makedirs(args.cache_dir, exist_ok=True)
    try:
        os.chmod(args.cache_dir, 0o700)
    except Exception:
        pass

    # Read event from GITHUB_EVENT_PATH
    event = {}
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, 'r') as f:
                event = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load event payload from GITHUB_EVENT_PATH: {e}")

    # Run DeepSeek CI
    result = run_ci(
        event=event,
        workspace=args.workspace,
        operator_token=os.environ.get('OPERATOR_TOKEN')
    )

    # Secure output serialization with 0o600 permissions
    output_path = Path('deepseek_output.json')
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = 0o600
    try:
        fd = os.open(output_path, flags, mode)
        with open(fd, 'w') as f:
            json.dump(result, f, indent=2)
    except Exception:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

    try:
        os.chmod(output_path, 0o600)
    except Exception:
        pass

    print(f"✅ CI run completed. Decisions: {result.get('actions', [])}")

if __name__ == '__main__':
    main()
