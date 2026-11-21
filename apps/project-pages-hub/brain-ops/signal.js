/* Brain BioFeedBack signal renderer.
 * Source: the page's existing GitHub Actions workflow-run response.
 * Each marker is a discrete software event, never a synthesized waveform.
 */
(function (root) {
  "use strict";

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char];
    });
  }

  function statusClass(run) {
    var status = String(run.conclusion || run.status || "unknown").toLowerCase();
    if (status === "success") return "success";
    if (status === "failure" || status === "timed_out" || status === "action_required") return "failure";
    if (status === "cancelled" || status === "startup_failure") return "cancelled";
    if (status === "queued" || status === "in_progress" || status === "waiting" || status === "requested" || status === "pending") return "pending";
    return "unknown";
  }

  function durationLabel(run) {
    var start = Date.parse(run.run_started_at || "");
    var end = Date.parse(run.updated_at || "");
    if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) return "pending";
    var seconds = Math.round((end - start) / 1000);
    return seconds + "s";
  }

  function render(runs, width) {
    var observations = (Array.isArray(runs) ? runs : []).filter(function (run) {
      return run && Number.isFinite(Date.parse(run.created_at || ""));
    }).map(function (run) {
      return {
        run: run,
        time: Date.parse(run.created_at),
        lane: String(run.name || "Brain workflow")
      };
    }).sort(function (a, b) {
      return a.time - b.time;
    });

    if (!observations.length) {
      return '<p class="empty">No observed Brain workflow events in the current API window.</p>';
    }

    var chartWidth = Number.isFinite(width) && width >= 640 ? Math.round(width) : 1000;
    var labelWidth = 230;
    var rightPad = 24;
    var topPad = 28;
    var laneHeight = 32;
    var bottomPad = 42;
    var lanes = Array.from(new Set(observations.map(function (item) { return item.lane; }))).sort();
    var chartHeight = topPad + lanes.length * laneHeight + bottomPad;
    var minTime = observations[0].time;
    var maxTime = observations[observations.length - 1].time;
    var timeSpan = Math.max(1, maxTime - minTime);
    var plotWidth = chartWidth - labelWidth - rightPad;
    var x = function (time) { return labelWidth + ((time - minTime) / timeSpan) * plotWidth; };
    var parts = [
      '<svg class="brain-signal-chart" viewBox="0 0 ' + chartWidth + ' ' + chartHeight + '" role="img" aria-label="Brain workflow event raster across time">',
      '<text class="signal-axis-title" x="' + labelWidth + '" y="13">Workflow event time (UTC) · oldest → newest</text>'
    ];

    for (var tick = 0; tick <= 4; tick += 1) {
      var tickTime = minTime + (timeSpan * tick / 4);
      var tickX = x(tickTime);
      var tickLabel = new Date(tickTime).toISOString().slice(0, 16).replace("T", " ");
      parts.push('<line class="signal-grid" x1="' + tickX.toFixed(1) + '" y1="' + (topPad - 8) + '" x2="' + tickX.toFixed(1) + '" y2="' + (chartHeight - bottomPad + 4) + '"/>');
      parts.push('<text class="signal-tick" x="' + tickX.toFixed(1) + '" y="' + (chartHeight - 12) + '" text-anchor="middle">' + tickLabel + '</text>');
    }

    lanes.forEach(function (lane, laneIndex) {
      var centerY = topPad + laneIndex * laneHeight + laneHeight / 2;
      parts.push('<text class="signal-lane" x="8" y="' + (centerY + 4) + '">' + escapeHtml(lane.slice(0, 32)) + '</text>');
      parts.push('<line class="signal-lane-guide" x1="' + labelWidth + '" y1="' + centerY + '" x2="' + (chartWidth - rightPad) + '" y2="' + centerY + '"/>');
    });

    observations.forEach(function (item) {
      var laneIndex = lanes.indexOf(item.lane);
      var centerY = topPad + laneIndex * laneHeight + laneHeight / 2;
      var markerX = x(item.time);
      var run = item.run;
      var state = String(run.conclusion || run.status || "unknown");
      var title = [
        item.lane,
        "#" + String(run.run_number == null ? "?" : run.run_number),
        state,
        new Date(item.time).toISOString(),
        "duration " + durationLabel(run),
        "SHA " + String(run.head_sha || "unavailable").slice(0, 12)
      ].join(" · ");
      parts.push('<line class="signal-pulse signal-' + statusClass(run) + '" x1="' + markerX.toFixed(1) + '" y1="' + (centerY - 8) + '" x2="' + markerX.toFixed(1) + '" y2="' + (centerY + 8) + '"><title>' + escapeHtml(title) + '</title></line>');
    });

    parts.push('</svg>');
    return parts.join("");
  }

  var api = { render: render };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.BrainSignal = api;
}(typeof globalThis !== "undefined" ? globalThis : this));
