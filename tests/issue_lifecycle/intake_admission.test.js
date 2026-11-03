'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { classifyIssueEvent } = require('../../scripts/issue_lifecycle/intake_admission');

function event(overrides = {}) {
  return {
    action: 'opened',
    sender: { login: 'maintainer', type: 'User' },
    issue: {
      title: 'A bounded issue',
      body: 'Details',
      author_association: 'MEMBER',
      user: { login: 'maintainer' },
    },
    ...overrides,
  };
}

test('admits trusted normal-volume author for advisory triage', () => {
  assert.equal(classifyIssueEvent(event(), 1).decision, 'advisory_triage');
});

test('keeps public issue filing but excludes untrusted author from provider route', () => {
  const result = classifyIssueEvent(event({ issue: { ...event().issue, author_association: 'NONE' } }), 1);
  assert.equal(result.decision, 'deterministic_only');
  assert.equal(result.reason, 'untrusted_association');
});

test('filters bot actors from provider route', () => {
  const result = classifyIssueEvent(event({ sender: { login: 'renovate[bot]', type: 'Bot' } }), 1);
  assert.equal(result.reason, 'non_user_actor');
});

test('does not trust a different actor reopening an issue without actor permission evidence', () => {
  const result = classifyIssueEvent(event({ action: 'reopened', sender: { login: 'other-member', type: 'User' } }), 1);
  assert.equal(result.reason, 'actor_author_mismatch');
});

test('routes burst authors to deterministic-only lane', () => {
  const result = classifyIssueEvent(event(), 4);
  assert.equal(result.reason, 'actor_burst_threshold');
});

test('routes oversized payloads to deterministic-only lane', () => {
  const issue = { ...event().issue, body: 'x'.repeat(20_001) };
  assert.equal(classifyIssueEvent(event({ issue }), 1).reason, 'oversized_payload');
});

test('fails closed on malformed events and unknown quota/count evidence', () => {
  assert.equal(classifyIssueEvent({}, 0).reason, 'malformed_event');
  assert.equal(classifyIssueEvent(event(), -1).reason, 'actor_burst_threshold');
});

test('rejects unsupported actions', () => {
  assert.equal(classifyIssueEvent(event({ action: 'edited' }), 1).reason, 'unsupported_action');
});
