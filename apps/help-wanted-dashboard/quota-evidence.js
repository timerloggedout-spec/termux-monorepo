/* Public display only: never runtime admission or private account telemetry. */
(function (root) {
  'use strict';
  const MAX_AGE_MS = 15 * 60 * 1000;
  const STATUS = new Set(['ok', 'watch', 'exhausted', 'cap_tripped']);
  function timestamp(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT.*(?:Z|[+-]\d\d:\d\d)$/.test(value)) return NaN;
    return Date.parse(value);
  }
  function readingView(service, reading, now = Date.now()) {
    if (!reading) return {status: 'unknown', note: 'No observation supplied.'};
    const observed = timestamp(reading.observed_at);
    if (!Number.isFinite(observed) || observed > now) return {status: 'unknown', note: 'Missing or invalid observation time; snapshot generation is not an observation.'};
    if (now - observed > MAX_AGE_MS) return {status: 'stale', note: 'Historical observation; refetch authoritative evidence before acting.'};
    const reset = timestamp(reading.reset);
    if (reading.reset != null && (!Number.isFinite(reset) || reset <= now)) return {status: 'unknown', note: 'Reset boundary is unverified or passed; no reset is inferred.'};
    if (reading.horizon !== 'H0' || reading.evidence_status !== 'confirmed') return {status: 'reported', note: 'Attributed report, not a confirmed live reading.'};
    if (!STATUS.has(reading.status)) return {status: 'unknown', note: 'No supported current state supplied.'};
    return {status: reading.status, note: 'Recent confirmed observation; not permission to spend or dispatch.'};
  }
  function indexReadings(rows) {
    const index = Object.create(null);
    for (const row of Array.isArray(rows) ? rows : []) {
      if (!row || typeof row.resource_id !== 'string') continue;
      const id = row.resource_id.replace(/^quota:/, '');
      // Duplicates are ambiguous; never let ordering select a healthy state.
      index[id] = Object.prototype.hasOwnProperty.call(index, id) ? null : row;
    }
    return index;
  }
  function mappingCapabilityCounts(rows, supplied) {
    const keys = ['actual_mapping', 'passive_parser', 'documentation_only', 'unknown_or_unsupported'];
    const counts = Object.fromEntries(keys.map(key => [key, 0]));
    for (const row of Array.isArray(rows) ? rows : []) {
      const status = mappingCapability(row).status;
      const key = status === 'actual_quota_service_mapping' ? 'actual_mapping' :
        status === 'implemented_passive_parser' ? 'passive_parser' :
        status === 'documentation_only' ? 'documentation_only' : 'unknown_or_unsupported';
      counts[key] += 1;
    }
    // Trust source counts only when explicitly typed and non-negative; otherwise derive from rows.
    if (supplied && typeof supplied === 'object') for (const key of keys)
      if (Number.isInteger(supplied[key]) && supplied[key] >= 0) counts[key] = supplied[key];
    return counts;
  }
  function mappingCapability(row) {
    const raw = row && row.quota_mapping;
    if (!raw || typeof raw !== 'object') return {status:'unknown_or_unsupported', dimensions:'unknown', source_kind:'none_verified'};
    const allowed = new Set(['actual_quota_service_mapping','implemented_passive_parser','documentation_only','unsupported_or_unknown']);
    return {
      status: allowed.has(raw.status) ? raw.status : 'unknown_or_unsupported',
      dimensions: typeof raw.dimensions === 'string' ? raw.dimensions : 'unknown',
      source_kind: typeof raw.source_kind === 'string' ? raw.source_kind : 'none_verified'
    };
  }
  function coverageView(row) {
    if (!row || typeof row !== 'object') return {mapping: 'unknown', evidence: 'unknown', balance: 'not_published'};
    return {
      mapping: typeof row.mapping_state === 'string' ? row.mapping_state : 'unknown',
      evidence: typeof row.evidence_state === 'string' ? row.evidence_state : 'unknown',
      scope: typeof row.scope === 'string' ? row.scope : (typeof row.key_scope === 'string' ? row.key_scope : 'unknown'),
      quotaKind: typeof row.quota_kind === 'string' ? row.quota_kind : 'unknown',
      documentedLimit: row.documented_limit ?? null,
      freeEntitlement: row.free_entitlement ?? null,
      balance: 'not published',
      mappingCapability: mappingCapability(row)
    };
  }
  const api = {MAX_AGE_MS, readingView, indexReadings, coverageView, mappingCapability, mappingCapabilityCounts};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.QuotaEvidence = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
