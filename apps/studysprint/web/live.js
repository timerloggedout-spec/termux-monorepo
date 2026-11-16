/* Opt-in live mode for the web surface (branch (a)) -- the JS
 * mirror of live.py; the two must stay contract-identical.
 *
 * Default OFF. When the user enables it (persisted in
 * localStorage ss.live_mode), the surface calls the deployed
 * Strands endpoint under the strands-aws contract
 * (strands-aws/schemas/endpoint.schema.json):
 *   GET  {endpoint}/health  -- also the A2 wake-ping, fired on
 *                              load when live mode is on (host B
 *                              cold wake measured 34.2s; the
 *                              ~60s envelope is UX, not an error)
 *   POST {endpoint}/plan    -- ALWAYS a receipt; endpoint-side
 *                              failures arrive as execution_class=
 *                              offline-gate + fail_closed=true.
 * If the endpoint is UNREACHABLE, the surface keeps its built-in
 * deterministic core rendering (already in #plan-body) and stamps
 * a surface-local fallback receipt -- never dressed as live:
 * production receipts are execution_class=live-production with
 * deployment=true and the Bedrock model block. */
"use strict";

const SS_LIVE_ENDPOINT =
  "https://hostb-live-5b9d7.containers.snapdeploy.app";
const SS_HEALTH_TIMEOUT_MS = 70000;
const SS_PLAN_TIMEOUT_MS = 120000;

function ssLiveEnabled() {
  try { return localStorage.getItem("ss.live_mode") === "1"; }
  catch (e) { return false; }
}

function ssFallbackReceipt(error) {
  return {
    execution_class: "offline-gate",
    fail_closed: true,
    deployment: false,
    model: null,
    source: "surface-local",
    error: String(error),
  };
}

async function ssFetch(path, method, body, timeoutMs) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const resp = await fetch(SS_LIVE_ENDPOINT + path, {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
      signal: ctl.signal,
    });
    if (resp.status !== 200) throw new Error("HTTP " + resp.status);
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

async function ssWake() {
  try {
    const health = await ssFetch("/health", "GET", null,
                                 SS_HEALTH_TIMEOUT_MS);
    return { awake: true, health };
  } catch (e) {
    return { awake: false, error: String(e) };
  }
}

async function ssLivePlan(syllabusRef) {
  if (!ssLiveEnabled()) return ssFallbackReceipt("live mode off");
  try {
    const receipt = await ssFetch(
      "/plan", "POST",
      { syllabus_ref: syllabusRef || "examples/syllabus.json" },
      SS_PLAN_TIMEOUT_MS);
    if (!receipt || typeof receipt !== "object" ||
        !("execution_class" in receipt)) {
      throw new Error("malformed receipt body");
    }
    return receipt;
  } catch (e) {
    return ssFallbackReceipt(e && e.message ? e.message : e);
  }
}

function ssStampLiveReceipt(receipt) {
  try {
    const log = JSON.parse(
      localStorage.getItem("ss.live_receipts") || "[]");
    log.push({ at: new Date().toISOString(), receipt });
    localStorage.setItem("ss.live_receipts",
                         JSON.stringify(log.slice(-20)));
  } catch (e) { /* storage full/blocked: the panel still shows it */ }
}

function ssReceiptLine(r) {
  const model = r.model
    ? `${r.model.provider}/${r.model.model_id}` : "no model";
  return `execution_class=${r.execution_class} · ` +
    `deployment=${r.deployment} · ${model}` +
    (r.fail_closed ? " · fail_closed=true" : "") +
    (r.source ? ` · source=${r.source}` : "");
}

function ssMountLivePanel() {
  const anchor = document.querySelector("#plan-body");
  if (!anchor || document.querySelector("#live-panel")) return;
  const panel = document.createElement("section");
  panel.id = "live-panel";
  panel.style.cssText =
    "border:1px solid #8884;border-radius:8px;padding:10px;" +
    "margin:10px 0;font-size:0.92em";
  panel.innerHTML =
    `<label><input type="checkbox" id="live-toggle"> ` +
    `Live mode (Bedrock endpoint)</label> ` +
    `<span id="live-status"></span><br>` +
    `<button id="live-run" type="button">Run live plan</button>` +
    `<pre id="live-out" style="white-space:pre-wrap"></pre>`;
  anchor.parentNode.insertBefore(panel, anchor);

  const toggle = panel.querySelector("#live-toggle");
  const status = panel.querySelector("#live-status");
  const out = panel.querySelector("#live-out");
  toggle.checked = ssLiveEnabled();
  const armWake = async () => {
    if (!ssLiveEnabled()) { status.textContent = ""; return; }
    status.textContent = " · waking endpoint…";
    const w = await ssWake();
    status.textContent = w.awake
      ? ` · endpoint awake (deployment=${w.health.deployment}, ` +
        `model=${w.health.model_id || "?"})`
      : " · endpoint unreachable — core fallback armed";
  };
  toggle.addEventListener("change", () => {
    try {
      localStorage.setItem("ss.live_mode", toggle.checked ? "1" : "0");
    } catch (e) { /* private mode: toggle still works in-session */ }
    armWake();
  });
  panel.querySelector("#live-run").addEventListener("click",
    async (ev) => {
      const btn = ev.currentTarget;
      btn.disabled = true;
      out.textContent = ssLiveEnabled()
        ? "calling the endpoint (wake + invoke can take ~60s)…"
        : "live mode is off — showing the built-in core plan.";
      const receipt = await ssLivePlan();
      ssStampLiveReceipt(receipt);
      out.textContent = receipt.source === "surface-local"
        ? ssReceiptLine(receipt) +
          "\nEndpoint unreachable — the plan above is the built-in " +
          "deterministic core plan. Nothing was fabricated live."
        : ssReceiptLine(receipt) + "\n" +
          JSON.stringify(receipt.plan || receipt, null, 2)
            .slice(0, 1200);
      btn.disabled = false;
    });
  armWake();
}

window.SS_Live = {
  ENDPOINT: SS_LIVE_ENDPOINT,
  enabled: ssLiveEnabled,
  wake: ssWake,
  plan: ssLivePlan,
  fallbackReceipt: ssFallbackReceipt,
};
document.addEventListener("DOMContentLoaded", ssMountLivePanel);
