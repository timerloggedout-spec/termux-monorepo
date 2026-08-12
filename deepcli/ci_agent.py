"""
CI agent logic for DeepSeek integration.
Does not modify core.py – used by ci_mode.py.

Admin-scope defaults: thinking=True, expert=True (always).
No quota model — frustrated-user retries only.
"""
import os
import subprocess
import requests


def deepseek_chat(session, messages, thinking=True, expert=True):
    """
    Send a chat request to DeepSeek using the authenticated session.
    --thinking and --Expert are ALWAYS true by default (operator policy).
    """
    headers = {
        'Authorization': f"Bearer {session['token']}",
        'Content-Type': 'application/json',
    }
    s = requests.Session()
    s.cookies.update(session.get('cookies', {}))
    s.headers.update(headers)

    payload = {
        'messages': messages,
        'stream': False,
        'thinking': bool(thinking),
        'expert': bool(expert),
    }
    resp = s.post(
        'https://chat.deepseek.com/api/chat/completions',
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    try:
        return data['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected DeepSeek response shape: {e}; body keys={list(data) if isinstance(data, dict) else type(data)}") from e


def run_ci(event, session, peer, workspace, operator_token):
    """
    Non-interactive agent loop.
    Returns a dict of actions taken.
    """
    gh_env = os.environ.copy()
    if operator_token:
        gh_env['GH_TOKEN'] = operator_token

    pr_number = event.get('pull_request', {}).get('number')
    repo = event.get('repository', {}).get('full_name')
    action = event.get('action')
    decisions = []

    # Always-true defaults (operator policy for this DeepSeek path)
    thinking = os.environ.get('DEEPSEEK_THINKING', 'true').lower() not in ('0', 'false', 'no')
    expert = os.environ.get('DEEPSEEK_EXPERT', 'true').lower() not in ('0', 'false', 'no')

    if action in ['opened', 'synchronize', 'reopened'] and pr_number:
        if not repo:
            return {'actions': [], 'error': 'Missing repository.full_name in event'}

        try:
            diff = subprocess.check_output(
                ['gh', 'pr', 'diff', str(pr_number), '--repo', repo],
                env=gh_env, text=True, timeout=120,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return {'actions': [], 'error': f'Failed to get PR diff: {e}'}

        truncated = len(diff) > 8000
        user_content = diff[:8000]
        if truncated:
            user_content += '\n\n[diff truncated; remainder omitted]'

        messages = [
            {
                'role': 'system',
                'content': (
                    'You are a senior software engineer reviewing a pull request. '
                    'Provide a concise summary of potential issues, risks, and improvements. '
                    'Use expert reasoning and explicit thinking steps.'
                ),
            },
            {'role': 'user', 'content': user_content},
        ]

        try:
            analysis = deepseek_chat(session, messages, thinking=thinking, expert=expert)
        except Exception as e:
            # Public-safe message; details stay in job logs via raise path callers may log
            analysis = f"DeepSeek API error: {type(e).__name__}"

        comment_ok = False
        try:
            r = subprocess.run(
                ['gh', 'pr', 'comment', str(pr_number), '--body', analysis[:2000], '--repo', repo],
                env=gh_env, check=False, timeout=60,
            )
            comment_ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            comment_ok = False

        if comment_ok:
            decisions.append({
                'type': 'pr_review',
                'pr': pr_number,
                'summary': analysis[:200],
                'thinking': thinking,
                'expert': expert,
            })

    return {
        'actions': decisions,
        'event': action,
        'pr': pr_number,
        'provider_used': peer.get('provider', 'deepseek'),
        'thinking': thinking,
        'expert': expert,
    }
