#!/usr/bin/env node
'use strict';

// Cheap, provider-independent admission policy for public issue events.
// This is a cost/abuse signal, not a spam verdict or issue resolver.
const TRUSTED_ASSOCIATIONS = new Set(['OWNER', 'MEMBER', 'COLLABORATOR']);
const MAX_TITLE_CHARS = 256;
const MAX_BODY_CHARS = 20_000;
const MAX_ISSUES_PER_ACTOR_WINDOW = 3;

function classifyIssueEvent(event, recentIssueCount) {
  if (!event || typeof event !== 'object' || !event.issue || !event.sender) {
    return { decision: 'deterministic_only', reason: 'malformed_event', trust: 'unknown' };
  }

  const issue = event.issue;
  const sender = event.sender;
  const author = issue.user || {};
  const association = String(issue.author_association || 'NONE').toUpperCase();
  const trust = TRUSTED_ASSOCIATIONS.has(association) ? 'trusted_association' : 'public_untrusted';

  if (!['opened', 'reopened'].includes(event.action)) {
    return { decision: 'deterministic_only', reason: 'unsupported_action', trust };
  }
  if (sender.type !== 'User') {
    return { decision: 'deterministic_only', reason: 'non_user_actor', trust };
  }
  if (!author.login || sender.login !== author.login) {
    return { decision: 'deterministic_only', reason: 'actor_author_mismatch', trust };
  }
  if (!TRUSTED_ASSOCIATIONS.has(association)) {
    return { decision: 'deterministic_only', reason: 'untrusted_association', trust };
  }
  if (String(issue.title || '').length > MAX_TITLE_CHARS ||
      String(issue.body || '').length > MAX_BODY_CHARS) {
    return { decision: 'deterministic_only', reason: 'oversized_payload', trust };
  }
  const count = Number.isInteger(recentIssueCount) && recentIssueCount >= 0
    ? recentIssueCount : Number.MAX_SAFE_INTEGER;
  if (count > MAX_ISSUES_PER_ACTOR_WINDOW) {
    return { decision: 'deterministic_only', reason: 'actor_burst_threshold', trust, recent_issue_count: count };
  }

  return {
    decision: 'advisory_triage',
    reason: 'trusted_normal_volume',
    trust,
    recent_issue_count: count,
  };
}

if (require.main === module) {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  if (!eventPath) throw new Error('GITHUB_EVENT_PATH is required');
  const fs = require('node:fs');
  const event = JSON.parse(fs.readFileSync(eventPath, 'utf8'));
  const count = Number.parseInt(process.env.RECENT_ISSUE_COUNT || '', 10);
  const result = classifyIssueEvent(event, Number.isInteger(count) ? count : -1);
  const output = process.env.GITHUB_OUTPUT;
  if (output) {
    fs.appendFileSync(output, Object.entries(result)
      .map(([key, value]) => `${key}=${String(value)}`)
      .join('\\n') + '\\n');
  }
  process.stdout.write(JSON.stringify(result) + '\\n');
}

module.exports = { classifyIssueEvent };
