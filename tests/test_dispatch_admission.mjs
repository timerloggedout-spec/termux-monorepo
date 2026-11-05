// Tests for scripts/ci/dispatch_admission.js — issue #3812 step 4 matrix.
// Run: node --test tests/test_dispatch_admission.mjs
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const admission = require('../scripts/ci/dispatch_admission.js');
const { evaluateAdmission, bucketRuns, OUTPUT_LANES } = admission;

const P = (byWorkflow) => ({ byWorkflow });

// 1. Empty backlog: everything admitted, nothing in flight.
test('empty backlog admits every gated output', () => {
  const r = evaluateAdmission({ pressure: P({}), force: false });
  assert.equal(r.global_inflight, 0);
  for (const rec of r.records) {
    assert.equal(rec.admitted, true, rec.lane);
    assert.equal(rec.reason, 'admitted');
    assert.equal(rec.lane_inflight, 0);
    assert.equal(rec.global_inflight, 0);
  }
});

// 2. Unrelated backlog (THE regression case): heavy in-flight pressure
// in workflows that a target output does not wake must not suppress it.
// Under the old Node A rule, repo-wide busy >= 6 paused every lane.
test('unrelated backlog does not suppress a quiet lane', () => {
  const idToFile = new Map([
    [101, '.github/workflows/repo-gate.yml'], // unmanaged CI noise
    [102, '.github/workflows/ci-sweep.yml'], // managed, but not a member of dispatch_repochange
  ]);
  const runs = [
    ...Array.from({ length: 10 }, () => ({ workflow_id: 101 })),
    ...Array.from({ length: 5 }, () => ({ workflow_id: 102 })),
  ];
  const pressure = bucketRuns(runs, idToFile);
  assert.equal(pressure.total, 15); // old rule: busy=15 >= 6 -> all paused
  const r = evaluateAdmission({ pressure, force: false });
  const repochange = r.records.find((x) => x.lane === 'dispatch_repochange');
  assert.equal(repochange.admitted, true);
  assert.equal(repochange.reason, 'admitted');
  assert.equal(repochange.lane_inflight, 0);
  // global cap counts managed lanes only: ci-sweep x5 counts, repo-gate x10 does not
  assert.equal(r.global_inflight, 5);
});

// 3. Target-lane backlog: the output's own member at its class cap
// suppresses it with reason lane_cap and names the saturated workflow.
test('target-lane backlog suppresses with lane_cap', () => {
  const r = evaluateAdmission({
    pressure: P({ 'context-relationship-backfill': 2 }), force: false,
  });
  const hourly = r.records.find((x) => x.lane === 'dispatch_hourly');
  assert.equal(hourly.admitted, false);
  assert.equal(hourly.reason, 'lane_cap');
  assert.equal(hourly.saturated_workflow, 'context-relationship-backfill');
  assert.equal(hourly.lane_inflight, 2); // standard cap = 2
  // heavy class cap = 1: a single in-flight tribute-execute saturates hw_execute
  const r2 = evaluateAdmission({ pressure: P({ 'tribute-execute': 1 }), force: false });
  const exec = r2.records.find((x) => x.lane === 'dispatch_hw_execute');
  assert.equal(exec.admitted, false);
  assert.equal(exec.reason, 'lane_cap');
  assert.equal(exec.lane_inflight, 1);
});

// 4. Global cap: no member saturated, but managed in-flight total is at
// the hard cap -> suppression with reason global_cap.
test('hard global cap suppresses unsaturated lanes', () => {
  const byWorkflow = {
    'ci-sweep': 1, 'hygiene-sweep': 1, 'provider-availability': 1,
    'recon-intel-discovery': 1, 'team-mvt': 1, 'self-integrate': 1,
  };
  const r = evaluateAdmission({ pressure: P(byWorkflow), force: false });
  assert.equal(r.global_inflight, 6);
  const bridge = r.records.find((x) => x.lane === 'dispatch_bridge');
  assert.equal(bridge.lane_inflight, 0); // its own lanes are idle
  assert.equal(bridge.admitted, false);
  assert.equal(bridge.reason, 'global_cap');
  assert.equal(bridge.global_inflight, 6);
});

// 5. Stale-critical preemption: staleness at >= 2x threshold overrides
// both the lane cap and the global cap.
test('stale-critical lane preempts lane and global caps', () => {
  const r = evaluateAdmission({
    pressure: P({ 'tribute-execute': 1 }), // heavy cap reached
    force: false,
    staleness: { dispatch_hw_execute: { stale_min: 700, threshold_min: 300 } },
  });
  const exec = r.records.find((x) => x.lane === 'dispatch_hw_execute');
  assert.equal(exec.admitted, true);
  assert.equal(exec.reason, 'stale_critical_override');
  // and against a full global cap
  const byWorkflow = {
    'ci-sweep': 1, 'hygiene-sweep': 1, 'provider-availability': 1,
    'recon-intel-discovery': 1, 'team-mvt': 1, 'self-integrate': 1,
  };
  const r2 = evaluateAdmission({
    pressure: P(byWorkflow), force: false,
    staleness: { dispatch_q6: { stale_min: 1500, threshold_min: 720 } },
  });
  const q6 = r2.records.find((x) => x.lane === 'dispatch_q6');
  assert.equal(q6.admitted, true);
  assert.equal(q6.reason, 'stale_critical_override');
  // below 2x the same pressure still suppresses
  const r3 = evaluateAdmission({
    pressure: P(byWorkflow), force: false,
    staleness: { dispatch_q6: { stale_min: 1000, threshold_min: 720 } },
  });
  assert.equal(r3.records.find((x) => x.lane === 'dispatch_q6').admitted, false);
});

// 6. Force override: "all" admits everything regardless of pressure.
test('force override admits everything', () => {
  const byWorkflow = Object.fromEntries(
    Object.values(OUTPUT_LANES).flat().map((w) => [w, 9]));
  const r = evaluateAdmission({ pressure: P(byWorkflow), force: true });
  for (const rec of r.records) {
    assert.equal(rec.admitted, true, rec.lane);
    assert.equal(rec.reason, 'forced');
  }
});

// Matrix inventory is event-driven and must not be part of a timed dispatch tranche.
test('lane matrix inventory is not quota-dispatched', () => {
  assert.equal(
    Object.values(OUTPUT_LANES).flat().includes('ops-lane-matrix-sweep'),
    false,
  );
});

// The Tier-0 tree must react to state-changing events immediately while
// preserving scheduled phase slots only for the scheduled cadence wake.
test('quota dispatcher has demand wakes and schedule-only phase windows', () => {
  const workflow = readFileSync(
    new URL('../.github/workflows/quota-dispatch-tree.yml', import.meta.url),
    'utf8',
  );
  assert.match(workflow, /pull_request_target:/);
  assert.match(workflow, /workflow_run:\s+workflows:\s+\["lane events recorder"\]/);
  assert.match(workflow, /const firstCycle = context\.eventName === 'schedule'/);
  assert.match(workflow, /const eventDemand = \['pull_request_target', 'workflow_run', 'push'\]/);
  assert.match(workflow, /repoChanged && \(slow \|\| eventDemand\)/);
});

// 7. Rate-limit deferral: pressure read failed -> fail closed, every
// gated output suppressed with reason rate_limited (never dispatch blind).
test('rate-limit deferral fails closed', () => {
  const r = evaluateAdmission({ pressure: null, force: false });
  for (const rec of r.records) {
    assert.equal(rec.admitted, false, rec.lane);
    assert.equal(rec.reason, 'rate_limited');
  }
  // force still wins over a failed pressure read (emergency semantics)
  const r2 = evaluateAdmission({ pressure: null, force: true });
  for (const rec of r2.records) assert.equal(rec.admitted, true, rec.lane);
});
