import test from 'node:test';
import assert from 'node:assert/strict';
import { parseGraphImport } from '../src/graph-import.js';

const validEdge = {
  src: 'github:user:alice',
  dst: 'github:repository:demo',
  type: 'owns',
  evidence: {
    plane: 'github',
    record: 'repository:demo',
    method: 'api_observation',
    observed_at: '2026-11-05T12:00:00Z',
  },
};

test('parses valid JSON and normalizes node defaults', () => {
  const result = parseGraphImport(JSON.stringify({
    nodes: [{ id: 'github:user:alice', label: 'Alice' }],
    edges: [validEdge],
  }), 'graph.json');
  assert.equal(result.edges.length, 1);
  assert.equal(result.nodes[0].label, 'Alice');
  assert.equal(result.nodes[0].plane, 'github');
  assert.equal(result.nodes[0].description, 'Imported entity.');
});

test('rejects edges without complete provenance', () => {
  const broken = { ...validEdge, evidence: { ...validEdge.evidence } };
  delete broken.evidence.observed_at;
  assert.throws(() => parseGraphImport(JSON.stringify([broken]), 'edges.json'), /observed_at/);
});

test('preserves an explicitly unavailable timestamp as null', () => {
  const edge = { ...validEdge, evidence: { ...validEdge.evidence, observed_at: null } };
  const result = parseGraphImport(JSON.stringify([edge]), 'edges.json');
  assert.equal(result.edges[0].evidence.observed_at, null);
});

test('rejects null JSON with a useful format error', () => {
  assert.throws(() => parseGraphImport('null', 'graph.json'), /JSON object or edge array/);
});

test('rejects nodes without string identifiers and labels', () => {
  assert.throws(() => parseGraphImport(JSON.stringify({
    nodes: [{ id: 3, label: null }], edges: [validEdge],
  }), 'graph.json'), /string id and label/);
});

test('validates JSONL edges with the same provenance contract', () => {
  const broken = { ...validEdge, evidence: { ...validEdge.evidence, plane: 'unknown' } };
  assert.throws(() => parseGraphImport(JSON.stringify(broken), 'edges.jsonl'), /unsupported evidence plane/);
});

test('rejects malformed JSONL with the source line number', () => {
  assert.throws(() => parseGraphImport('{bad json}', 'edges.jsonl'), /line 1/);
});
