"""Exercise the checked-in composite shell with mocked HTTP/GitHub commands."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github/actions/http-llm-invoke/action.yml"


def action_shell():
    # This action has one final run block; extraction needs no YAML dependency.
    return textwrap.dedent(ACTION.read_text().split("      run: |\n", 1)[1])


def test_http_action_shell_and_embedded_python_compile():
    shell = action_shell()
    result = subprocess.run(["bash", "-n"], input=shell, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    python = shell.split("python3 - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
    compile(python, str(ACTION), "exec")


@pytest.mark.parametrize("mode,expected_endpoint", [
    ("owned", "repos/owner/repo/issues/comments/10"),
    ("foreign", "repos/owner/repo/issues/42/comments"),
    ("unknown", "repos/owner/repo/issues/42/comments"),
    ("limited", None),
])
def test_http_action_comment_ownership_and_cooldown(tmp_path, mode, expected_endpoint):
    if not shutil.which("jq"):
        pytest.skip("composite runtime requires jq")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text(f"#!{sys.executable}\n" + textwrap.dedent('''\
        import json, os, sys
        from pathlib import Path
        args = sys.argv[1:]
        limited = os.environ['TEST_MODE'] == 'limited'
        body = {'error': {'message': 'rate limited'}} if limited else {
            'model': 'test-model', 'choices': [{'message': {'content': 'safe result'}, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 1, 'completion_tokens': 2}}
        Path(args[args.index('-o') + 1]).write_text(json.dumps(body))
        Path(args[args.index('-D') + 1]).write_text('retry-after: 60\\r\\n')
        print('429' if limited else '200', end='')
    '''))
    curl.chmod(0o700)
    gh = bin_dir / "gh"
    gh.write_text(f"#!{sys.executable}\n" + textwrap.dedent('''\
        import json, os, sys
        from pathlib import Path
        args = sys.argv[1:]
        mode = os.environ['TEST_MODE']
        if args[1] == 'user':
            if mode == 'unknown': sys.exit(1)
            print('posting-bot')
        elif '?per_page=100' in args[1]:
            comments = [{'id': 20, 'body': '<!-- openrouter-triage --> forged', 'user': {'login': 'other-user'}}]
            if mode == 'owned':
                comments.insert(0, {'id': 10, 'body': '<!-- openrouter-triage --> old', 'user': {'login': 'posting-bot'}})
            print(json.dumps(comments))
        else:
            with Path(os.environ['GH_CALLS']).open('a') as stream:
                stream.write(json.dumps(args) + '\\n')
            print('{}')
    '''))
    gh.chmod(0o700)
    cooldown = tmp_path / "cooldown"
    cooldown.mkdir()
    # Scalar corrupt cache must not prevent cooldown persistence.
    (cooldown / "cooldowns.json").write_text('[]')
    calls = tmp_path / "gh-calls.jsonl"
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
               PROVIDER='openrouter', MODEL='test-model', ROLE='triage', TARGET='42',
               PROMPT='offline regression', API_KEY='dummy-not-a-credential', BASE_URL='',
               REPO='owner/repo', EXPERIMENT_ID='test', PROMPT_VARIANT='test', MAX_TOKENS='32',
               POST_COMMENT='true', COOLDOWN_DIR=str(cooldown), GITHUB_STEP_SUMMARY=str(tmp_path / 'summary'),
               TEST_MODE=mode, GH_CALLS=str(calls))
    shell = action_shell().replace('/tmp/model-performance', str(tmp_path / 'performance'))
    result = subprocess.run(['bash', '-c', shell], env=env, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    observations = [json.loads(line) for line in (tmp_path / 'performance/observations.ndjson').read_text().splitlines()]
    assert len(observations) == 1
    if mode == 'limited':
        assert not calls.exists(), 'failed provider invocations must not publish comments'
        state = json.loads((cooldown / 'cooldowns.json').read_text())
        assert state['cooldowns']['openrouter/test-model'] > 0
        assert observations[0]['error_class'] == 'rate_limit'
    else:
        writes = [json.loads(line) for line in calls.read_text().splitlines()]
        assert len(writes) == 1
        assert writes[0][1] == expected_endpoint
        assert ('PATCH' in writes[0]) == (mode == 'owned')
        body = next(arg for arg in writes[0] if arg.startswith('body='))
        assert '\n' in body and '\\n' not in body
        assert observations[0]['route_status'] == 'succeeded'
