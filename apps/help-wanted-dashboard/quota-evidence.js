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
    if (service.lane === 'model') return {status: 'private', note: 'Private quota preflight required; public metadata is not admission evidence.'};
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
  const api = {MAX_AGE_MS, readingView, indexReadings};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.QuotaEvidence = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
