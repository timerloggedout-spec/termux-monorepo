'use strict';
/*
 * Lane-aware admission for the Quota Dispatch Tree (issue #3812, step 4).
 *
 * Replaces Node A's repo-wide admission guard ("busy >= 6 pauses every
 * lane") with per-lane pressure:
 *
 *   - Active runs are bucketed per workflow file, so a backlog in one
 *     lane no longer suppresses unrelated lanes.
 *   - Each managed workflow carries a class cap (heavy = 1 concurrent
 *     run, standard = 2). A verdict output is admitted only when every
 *     workflow it wakes is below its cap.
 *   - A retained HARD global cap (6) bounds total in-flight runs across
 *     all dispatcher-managed workflows. The cap's scope is corrected:
 *     it counts managed lanes only, never repo-wide CI noise.
 *   - Stale-critical preemption: a gated output whose staleness reaches
 *     2x its threshold is admitted despite lane and global caps, so a
 *     starved lane always self-heals (the G-02/G-03 lesson).
 *   - force ("all") admits everything, as before.
 *   - If the pressure read fails (rate limit / API error), admission
 *     fails closed: every gated output is suppressed with reason
 *     "rate_limited" instead of dispatching blind.
 *
 * Exempt outputs (never admission-gated, unchanged from the old tree):
 * dispatch_stall_watch (the watchdog itself) and dispatch_hw_refresh
 * (read-only refresh). They do not appear in the gated records.
 *
 * Every gated output produces a record:
 *   {lane, admitted, reason, lane_inflight, global_inflight,
 *    workflows, saturated_workflow?}
 * with reason one of: admitted | lane_cap | global_cap | rate_limited
 * | stale_critical_override | forced.
 * lane_inflight is the max in-flight count among the output's member
 * workflows; global_inflight is the managed-lane in-flight total.
 *
 * Tests: node --test tests/test_dispatch_admission.mjs
 */

const CLASS_CAPS = { heavy: 1, standard: 2 };
const GLOBAL_CAP = 6;
const STALE_FACTOR = 2;

// Workflow file base name (without .yml) -> admission class.
// heavy = lanes that spend or execute (the tree's Node F1 comment class);
// everything else managed is standard.
const LANE_CLASSES = {
  'tribute-followup': 'heavy',
  'tribute-scout': 'heavy',
  'tribute-execute': 'heavy',
  'tribute-llm-assist': 'heavy',
  'tribute-system1': 'heavy',
};

// Verdict output -> member workflow base names (mirrors the dispatch
// matrix in quota-dispatch-tree.yml; workflow_id is "<lane>.yml").
const OUTPUT_LANES = {
  dispatch_bridge: ['tunnel-canary', 'deepcli-agent-bridge'],
  dispatch_probe: ['tailscale-bridge-probe'],
  dispatch_eval: ['continuous-evaluation', 'team-mvt'],
  dispatch_recon: ['recon-intel-discovery'],
  dispatch_hw_pair: ['tribute-followup', 'tribute-scout'],
  dispatch_hw_execute: ['tribute-execute'],
  dispatch_hw_assist: ['tribute-llm-assist'],
  dispatch_hourly: [
    'merge-promotion-queue-v3', 'agent-continuous-ops',
    'cellcog-engineering-health', 'issue-observatory',
    'reconciliation-engine', 'historical-evaluation-correlation',
    'vercel-batch-deploy', 'context-relationship-backfill',
  ],
  dispatch_repochange: [
    'automation-docs-continuous-refresh', 'context-relationship-audit',
  ],
  dispatch_q3: ['tribute-system1'],
  dispatch_q4: ['cadence-lead-lag', 'self-integrate'],
  dispatch_q6: [
    'ci-sweep', 'hygiene-sweep',
    'provider-availability', 'actions-queue-reaper',
    'gitlab-governed-reconciliation',
  ],
  dispatch_vantage: ['vantage-cost-report'],
};

const GATED_OUTPUTS = Object.keys(OUTPUT_LANES);
const MANAGED_WORKFLOWS = [...new Set(Object.values(OUTPUT_LANES).flat())];

function laneCap(workflowBase) {
  return CLASS_CAPS[LANE_CLASSES[workflowBase] || 'standard'];
}

// Bucket active runs by workflow file base name.
// runs: workflow-run objects carrying workflow_id (numeric).
// idToFile: Map/object of workflow_id -> ".github/workflows/<base>.yml"
// (or a bare "<base>.yml"). Runs whose workflow is unknown are ignored.
function bucketRuns(runs, idToFile) {
  const byWorkflow = {};
  let total = 0;
  for (const run of runs || []) {
    const raw = idToFile instanceof Map ? idToFile.get(run.workflow_id) : idToFile[run.workflow_id];
    if (!raw) continue;
    const base = String(raw).split('/').pop().replace(/\.yml$/, '');
    byWorkflow[base] = (byWorkflow[base] || 0) + 1;
    total += 1;
  }
  return { byWorkflow, total };
}

// Evaluate admission for every gated output.
// input.pressure: {byWorkflow} from bucketRuns, or null when the
//   pressure read failed (rate limit / API error) -> fail closed.
// input.force: emergency "all" override.
// input.staleness: {outputName: {stale_min, threshold_min}} for outputs
//   with a staleness signal; stale-critical at stale_min >= 2x threshold.
function classifyPressureError(error) {
  const status = Number(error && (error.status || (error.response && error.response.status)) || 0);
  const headers = (error && error.response && error.response.headers)
    || (error && error.headers) || {};
  const remaining = headers['x-ratelimit-remaining'] || headers['X-RateLimit-Remaining'];
  const message = String(error && error.message || '').toLowerCase();
  if (status === 429 || remaining === '0'
      || /rate limit|secondary rate limit|abuse detection/.test(message)) {
    return 'rate_limited';
  }
  if (status === 401 || status === 403) return 'permission_denied';
  return 'api_error';
}

function evaluateAdmission(input) {
  const force = !!(input && input.force);
  const staleness = (input && input.staleness) || {};
  const pressure = input ? input.pressure : null;
  const pressureFailureReason = input && ['rate_limited', 'permission_denied', 'api_error'].includes(input.pressureFailureReason)
    ? input.pressureFailureReason : 'rate_limited';
  const byWorkflow = (pressure && pressure.byWorkflow) || {};
  const globalInflight = MANAGED_WORKFLOWS.reduce(
    (sum, w) => sum + (byWorkflow[w] || 0), 0);
  const admitted = {};
  const records = [];
  for (const output of GATED_OUTPUTS) {
    const workflows = OUTPUT_LANES[output];
    const laneInflight = Math.max(0, ...workflows.map((w) => byWorkflow[w] || 0));
    const record = {
      lane: output,
      workflows,
      lane_inflight: laneInflight,
      global_inflight: globalInflight,
    };
    if (force) {
      record.admitted = true;
      record.reason = 'forced';
    } else if (!pressure) {
      record.admitted = false;
      record.reason = pressureFailureReason;
    } else {
      const saturated = workflows.find((w) => (byWorkflow[w] || 0) >= laneCap(w));
      const s = staleness[output];
      const staleCritical = !!s && typeof s.stale_min === 'number'
        && typeof s.threshold_min === 'number' && s.threshold_min > 0
        && s.stale_min >= STALE_FACTOR * s.threshold_min;
      if (staleCritical && (saturated || globalInflight >= GLOBAL_CAP)) {
        record.admitted = true;
        record.reason = 'stale_critical_override';
        if (saturated) record.saturated_workflow = saturated;
      } else if (saturated) {
        record.admitted = false;
        record.reason = 'lane_cap';
        record.saturated_workflow = saturated;
      } else if (globalInflight >= GLOBAL_CAP) {
        record.admitted = false;
        record.reason = 'global_cap';
      } else {
        record.admitted = true;
        record.reason = 'admitted';
      }
    }
    admitted[output] = record.admitted;
    records.push(record);
  }
  return { admitted, records, global_inflight: globalInflight, global_cap: GLOBAL_CAP };
}

module.exports = {
  CLASS_CAPS, GLOBAL_CAP, STALE_FACTOR, LANE_CLASSES, OUTPUT_LANES,
  GATED_OUTPUTS, MANAGED_WORKFLOWS, laneCap, bucketRuns, classifyPressureError, evaluateAdmission,
};
