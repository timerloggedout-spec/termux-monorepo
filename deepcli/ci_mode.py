#!/usr/bin/env python3
"""
CI mode entrypoint – non-interactive agent.
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ci_agent import run_ci          # <-- changed from core to ci_agent
from session_manager import ensure_session


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', required=True)
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--cache-dir', required=True)
    args = parser.parse_args()

    os.environ['GITHUB_WORKSPACE'] = args.workspace
    session = ensure_session(cache_dir=args.cache_dir)

    try:
        event = json.loads(args.event)
    except json.JSONDecodeError:
        event = {}

    peer = {'provider': 'deepseek'}

    result = run_ci(
        event=event,
        session=session,
        peer=peer,
        workspace=args.workspace,
        operator_token=os.environ.get('OPERATOR_TOKEN'),
    )

    with open('deepseek_output.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ CI run completed. Decisions: {result.get('actions', [])}")


if __name__ == '__main__':
    main()
