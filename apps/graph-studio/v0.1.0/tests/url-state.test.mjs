import test from 'node:test';
import assert from 'node:assert/strict';
import { parseGraphUrlState } from '../src/url-state.js';

test('restores all shareable graph state from a copied URL', () => {
  const state = parseGraphUrlState('?view=network&q=agentic%20systems&plane=github&edge=owns&node=github%3Arepository%3Astudy');
  assert.deepEqual(state, {
    view: 'network',
    query: 'agentic systems',
    plane: 'github',
    edgeType: 'owns',
    selected: 'github:repository:study',
  });
});

test('normalizes invalid and missing URL state to safe defaults', () => {
  const state = parseGraphUrlState('?view=unknown&plane=not-a-plane');
  assert.deepEqual(state, {
    view: 'hierarchy',
    query: '',
    plane: 'all',
    edgeType: 'all',
    selected: 'github:repository:termux-monorepo',
  });
});
