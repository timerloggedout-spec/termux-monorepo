import json
from pathlib import Path
import subprocess

import pytest
import yaml

from scripts.proposals.feedback_api_diagnostics import classify

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {
    'X-RateLimit-Remaining': '0', 'X-RateLimit-Resource': 'core',
    'X-RateLimit-Limit': '5000', 'X-RateLimit-Used': '5000',
    'X-RateLimit-Reset': '1792479727',
}
MESSAGE = 'API rate limit exceeded for installation'


def test_original_failure_is_explicit_exhausted_installation_core_quota():
    assert classify(403, HEADERS, MESSAGE) == 'deferred_rate_limit'


@pytest.mark.parametrize('status,headers,message', [
    (403, HEADERS, 'Resource not accessible by integration'),
    (401, HEADERS, 'Bad credentials'),
    (429, HEADERS, 'Secondary rate limit'),
    (403, {**HEADERS, 'X-RateLimit-Remaining': '2'}, MESSAGE),
    (403, {**HEADERS, 'X-RateLimit-Used': '1'}, MESSAGE),
    (403, {k: v for k, v in HEADERS.items() if k != 'X-RateLimit-Reset'}, MESSAGE),
    (403, {**HEADERS, 'X-RateLimit-Resource': 'search'}, MESSAGE),
    (403, {}, MESSAGE),
])
def test_ambiguous_permission_and_auth_errors_are_not_called_installation_quota(status, headers, message):
    assert classify(status, headers, message) == 'error'
    assert run_workflow('files', status=status, headers=headers, message=message)['ok'] is False


def run_workflow(stage=None, status=403, headers=None, message=MESSAGE, already=False):
    workflow = yaml.safe_load((ROOT / '.github/workflows/proposal-lifecycle.yml').read_text())
    step = next(s for s in workflow['jobs']['vote-hygiene']['steps'] if 'script' in s.get('with', {}))
    harness = r'''
const fs = require('fs');
const cfg = JSON.parse(fs.readFileSync(0, 'utf8'));
const calls = [], outputs = {}, warnings = [], summary = [];
function maybe(stage) {
  calls.push(stage);
  if (stage === cfg.stage) {
    const error = new Error('synthetic API failure');
    error.status = cfg.status;
    error.response = {status: cfg.status, headers: cfg.headers, data: {message: cfg.message}};
    throw error;
  }
}
const github = {rest: {
  pulls: {listFiles: async () => { maybe('files'); return {data: [{filename: 'docs/proposals/active/example/ITEMS.md'}]}; }},
  issues: {
    listComments: async () => { maybe('comments'); return {data: cfg.already ? [{body: 'Proposal process checklist'}] : []}; },
    createComment: async () => { maybe('create'); return {data: {id: 123}}; }
  }
}};
const core = {
  setOutput: (k, v) => { outputs[k] = v; }, warning: m => warnings.push(m),
  summary: {addHeading: s => summary.push(s), addRaw: s => summary.push(s), write: async () => {}}
};
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
(async () => {
  try {
    await new AsyncFunction('github', 'context', 'core', 'require', cfg.script)(
      github, {repo: {owner: 'owner', repo: 'repo'}, issue: {number: 1}}, core, require);
    console.log(JSON.stringify({ok: true, calls, outputs, warnings, summary}));
  } catch (e) { console.log(JSON.stringify({ok: false, calls, outputs, status: e.status})); }
})();
'''
    payload = {'script': step['with']['script'], 'stage': stage, 'status': status,
               'headers': HEADERS if headers is None else headers, 'message': message, 'already': already}
    result = subprocess.run(['node', '-e', harness], input=json.dumps(payload), text=True,
                            capture_output=True, cwd=ROOT, check=True)
    return json.loads(result.stdout)


@pytest.mark.parametrize('stage', ['files', 'comments', 'create'])
def test_actual_workflow_defers_proved_quota_at_every_request_but_never_claims_posted(stage):
    result = run_workflow(stage)
    assert result['ok'] is True
    assert result['outputs']['feedback_status'] == 'deferred_rate_limit'
    assert 'not posted' in ' '.join(result['summary'])
    assert 'Actions job token' in ' '.join(result['summary'])
    assert result['calls'][-1] == stage
    assert result['warnings']


@pytest.mark.parametrize('status,message', [(403, 'Resource not accessible by integration'), (401, 'Bad credentials')])
def test_actual_workflow_still_fails_permission_and_auth_errors(status, message):
    result = run_workflow('files', status=status, message=message)
    assert result['ok'] is False and result['status'] == status
    assert 'feedback_status' not in result['outputs']


def test_posted_and_already_present_are_distinct_real_outcomes():
    posted = run_workflow()
    assert posted['outputs']['feedback_status'] == 'posted' and posted['calls'][-1] == 'create'
    existing = run_workflow(already=True)
    assert existing['outputs']['feedback_status'] == 'already_present'
    assert 'create' not in existing['calls']


def test_pr_workflow_keeps_vote_scan_and_never_receives_operator_secrets():
    text = (ROOT / '.github/workflows/proposal-lifecycle.yml').read_text()
    assert 'VOTE:' in text and 'MANIFEST Review log is the binding store' in text
    assert 'secrets.OPERATOR' not in text and 'pull_request_target' not in text
    workflow = yaml.safe_load(text)
    assert workflow['permissions'] == {'contents': 'read'}
    vote_job = workflow['jobs']['vote-hygiene']
    assert vote_job['permissions'] == {'contents': 'read', 'pull-requests': 'write'}
    assert all(not s.get('uses', '').startswith('actions/checkout') for s in vote_job['steps'])
    script = next(s['with']['script'] for s in vote_job['steps'] if 'script' in s.get('with', {}))
    assert 'child_process' not in script and 'execFile' not in script
    assert 'feedback_api_diagnostics.py' not in script
