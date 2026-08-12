"""
CI agent logic for DeepSeek integration.
Does not modify core.py – used by ci_mode.py.
"""
import os
import subprocess
import json
import requests


def deepseek_chat(session, messages):
    """
    Send a chat request to DeepSeek using the authenticated session.
    """
    headers = {
        'Authorization': f"Bearer {session['token']}",
        'Content-Type': 'application/json',
    }
    s = requests.Session()
    s.cookies.update(session.get('cookies', {}))
    s.headers.update(headers)

    payload = {'messages': messages, 'stream': False}
    resp = s.post('https://chat.deepseek.com/api/chat/completions', json=payload)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']


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

    if action in ['opened', 'synchronize', 'reopened'] and pr_number:
        try:
            diff = subprocess.check_output(
                ['gh', 'pr', 'diff', str(pr_number), '--repo', repo],
                env=gh_env, text=True
            )
        except subprocess.CalledProcessError as e:
            return {'actions': [], 'error': f'Failed to get PR diff: {e}'}

        messages = [
            {'role': 'system', 'content': 'You are a senior software engineer reviewing a pull request. Provide a concise summary of potential issues, risks, and improvements.'},
            {'role': 'user', 'content': diff[:8000]},
        ]

        try:
            analysis = deepseek_chat(session, messages)
        except Exception as e:
            analysis = f"DeepSeek API error: {e}"

        subprocess.run(
            ['gh', 'pr', 'comment', str(pr_number), '--body', analysis[:2000], '--repo', repo],
            env=gh_env, check=False
        )

        decisions.append({
            'type': 'pr_review',
            'pr': pr_number,
            'summary': analysis[:200],
        })

    return {
        'actions': decisions,
        'event': action,
        'pr': pr_number,
        'provider_used': peer.get('provider', 'deepseek'),
    }
