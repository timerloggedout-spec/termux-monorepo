/* chartkit.js - shared live-chart helpers for the dashboard family.
   Owner standard 2026-11-01 (docs/ops/DASHBOARD-CHART-STANDARD.md):
   every chart renders only from its page feed, carries the feed stamp
   and STALE state, and hardcodes nothing. Pure string builders so the
   pytest node-sim can pin them like quota-graphs' chartGeom. */
const CK = (() => {
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => '&#' + c.charCodeAt(0) + ';');
  const fmt = n => (typeof n === 'number' && isFinite(n)) ? (Math.round(n * 100) / 100).toLocaleString('en-US') : String(n ?? '');

  /* Horizontal bars: rows = [{label, value}]. Value labels double as
     the scale; the max is stated so a bar is never read unscaled. */
  function bars(rows, w = 640) {
    const data = (rows || []).filter(r => r && typeof r.value === 'number' && isFinite(r.value));
    if (!data.length) return '<p class="muted">No numeric data.</p>';
    const max = Math.max(...data.map(r => r.value), 0);
    const rowH = 20, labelW = 190, valW = 74, barW = Math.max(40, w - labelW - valW);
    const h = data.length * rowH + 18;
    const parts = ['<svg class="chart" viewBox="0 0 ' + w + ' ' + h + '" role="img">'];
    data.forEach((r, i) => {
      const y = i * rowH + 4, bw = max > 0 ? Math.max(1, (r.value / max) * barW) : 1;
      parts.push('<text x="0" y="' + (y + 12) + '" font-size="11">' + esc(String(r.label).slice(0, 30)) + '</text>');
      parts.push('<rect x="' + labelW + '" y="' + y + '" width="' + bw.toFixed(1) + '" height="12" fill="currentColor" opacity="0.75"><title>' + esc(r.label) + ' · ' + esc(fmt(r.value)) + '</title></rect>');
      parts.push('<text x="' + (labelW + bw + 6) + '" y="' + (y + 12) + '" font-size="11">' + esc(fmt(r.value)) + '</text>');
    });
    parts.push('<text x="' + labelW + '" y="' + (h - 2) + '" font-size="10" opacity="0.7">max ' + esc(fmt(max)) + '</text></svg>');
    return parts.join('');
  }

  /* Line chart with the legibility floor from the quota-graphs V2 fix:
     y ticks at min/mid/max and x labels at first/last timestamps -
     never an axis-less sparkline. points = [{t, v}]. */
  function line(points, w = 640, h = 180) {
    const pts = (points || []).filter(p => p && p.t)
      .map(p => ({ t: new Date(p.t).getTime(), v: (typeof p.v === 'number' && isFinite(p.v)) ? p.v : null, ts: p.t }))
      .filter(p => isFinite(p.t)).sort((a, b) => a.t - b.t);
    const values = pts.filter(p => p.v !== null).map(p => p.v);
    if (!values.length) return '<p class="muted">No observations on record.</p>';
    const padL = 52, padR = 10, padT = 10, padB = 20, iw = w - padL - padR, ih = h - padT - padB;
    const minV = Math.min(...values), maxV = Math.max(...values), midV = (minV + maxV) / 2;
    const minT = pts[0].t, maxT = pts[pts.length - 1].t, spanT = Math.max(1, maxT - minT), spanV = Math.max(1e-9, maxV - minV);
    const X = t => padL + (maxT === minT ? iw / 2 : (t - minT) / spanT * iw);
    const Y = v => padT + ih - (maxV === minV ? ih / 2 : (v - minV) / spanV * ih);
    const parts = ['<svg class="chart" viewBox="0 0 ' + w + ' ' + h + '" role="img" aria-label="Time series chart; missing observations are shown as gaps">'];
    [[maxV, Y(maxV)], [midV, Y(midV)], [minV, Y(minV)]].forEach(([v, y]) => {
      parts.push('<line x1="' + padL + '" y1="' + y + '" x2="' + (w - padR) + '" y2="' + y + '" stroke="currentColor" opacity="0.15"/>');
      parts.push('<text x="0" y="' + (y + 4) + '" font-size="11">' + esc(fmt(v)) + '</text>');
    });
    let segment = [];
    const flush = () => {
      if (segment.length > 1) {
        const path = segment.map((p, i) => (i ? 'L' : 'M') + X(p.t).toFixed(1) + ' ' + Y(p.v).toFixed(1)).join(' ');
        parts.push('<path d="' + path + '" fill="none" stroke="currentColor" stroke-width="1.5"/>');
      }
      segment = [];
    };
    pts.forEach(p => {
      if (p.v === null) { flush(); return; }
      segment.push(p);
      parts.push('<circle cx="' + X(p.t).toFixed(1) + '" cy="' + Y(p.v).toFixed(1) + '" r="3" fill="currentColor"><title>' + esc(p.ts) + ' · ' + esc(fmt(p.v)) + '</title></circle>');
    });
    flush();
    parts.push('<text x="' + padL + '" y="' + (h - 4) + '" font-size="10">' + esc(String(pts[0].ts).slice(0, 10)) + '</text>');
    parts.push('<text x="' + (w - padR) + '" y="' + (h - 4) + '" font-size="10" text-anchor="end">' + esc(String(pts[pts.length - 1].ts).slice(0, 10)) + '</text></svg>');
    return parts.join('');
  }

  /* STALE state for a feed stamp: 'fresh' | 'STALE' | 'unknown'. */
  function stampState(generatedAt, nowMs, thresholdMs = 86400000) {
    if (!generatedAt) return 'unknown';
    const t = new Date(generatedAt).getTime();
    if (!isFinite(t)) return 'unknown';
    return (nowMs - t) > thresholdMs ? 'STALE' : 'fresh';
  }

  return { esc, fmt, bars, line, stampState };
})();
if (typeof module !== 'undefined') module.exports = CK;
