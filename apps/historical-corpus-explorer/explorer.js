(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const state = { projection: null, nodes: [], edges: [], nodeIds: new Set(), edgeIds: new Set() };
  const MAX_RESULTS = 200;

  function text(id, value) {
    $(id).textContent = value === null || value === undefined || value === "" ? "Unavailable" : String(value);
  }
  function validObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }
  function safeCount(value) {
    return Number.isSafeInteger(value) && value >= 0 ? value.toLocaleString() : "Unavailable";
  }
  function showError(message) { $("input-error").textContent = message || ""; }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }
  function el(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = String(value);
    return node;
  }

  function renderProjection(p) {
    if (!validObject(p) || p.projection !== "historical_corpus_coverage" ||
        !validObject(p.provenance) || !validObject(p.coverage) ||
        !validObject(p.counts) || !validObject(p.reconciliation)) {
      throw new Error("Unsupported projection schema. Expected historical_corpus_coverage with provenance, coverage, counts, and reconciliation objects.");
    }
    state.projection = p;
    const cov = p.coverage;
    const prov = p.provenance;
    const rec = p.reconciliation;
    const status = typeof cov.status === "string" ? cov.status : "UNVERIFIED";
    text("status", status + (rec.status === "RECONCILIATION_REQUIRED" ? " · reconciliation required" : ""));
    $("status").style.borderColor = rec.error_count > 0 ? "var(--bad)" : rec.warning_count > 0 ? "var(--warn)" : "var(--good)";
    $("status").style.color = rec.error_count > 0 ? "var(--bad)" : rec.warning_count > 0 ? "var(--warn)" : "var(--good)";
    text("nodes", safeCount(p.counts.nodes));
    text("edges", safeCount(p.counts.edges));
    text("verified", safeCount(p.counts.verified_edges));
    text("candidate", safeCount(p.counts.candidate_edges));
    text("observed", prov.generated_at);
    text("continuation", cov.next_start_page === null ? "No cursor declared" : Number.isSafeInteger(cov.next_start_page) ? "Page " + cov.next_start_page : "Unverified");
    text("ref", prov.source_ref);
    text("sha", prov.source_sha);
    text("manifest-sha", prov.manifest_blob_sha);
    text("snapshot-id", p.snapshot_id);
    text("prov-state", prov.provenance_complete === true ? "Projection declares complete provenance; verify hashes against repository evidence before promotion." : "Provenance incomplete. Treat this projection as unverified.");
    $("load-note").textContent = "Projection loaded. Coverage is shown as declared by the source; reconciliation findings are separate and do not silently downgrade or upgrade it.";
    $("load-note").className = rec.error_count > 0 || rec.warning_count > 0 ? "notice" : "panel";
    const box = $("findings");
    clear(box);
    const findings = Array.isArray(rec.findings) ? rec.findings : [];
    if (!findings.length) {
      box.appendChild(el("div", "empty", "No reconciliation findings were supplied by this projection."));
      return;
    }
    findings.forEach((f) => {
      if (!validObject(f)) return;
      const card = el("div", "finding" + (f.severity === "error" ? " error" : ""));
      card.appendChild(el("strong", "", (f.severity || "finding").toUpperCase() + " · " + (f.code || "UNKNOWN_CODE")));
      card.appendChild(el("div", "", f.message || "No message supplied."));
      if (f.field) card.appendChild(el("div", "label", "Field: " + f.field));
      box.appendChild(card);
    });
  }

  function parseJsonl(content, label) {
    const rows = [];
    const seen = new Set();
    const lines = content.split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      let item;
      try { item = JSON.parse(lines[i]); }
      catch (_) { throw new Error(label + " line " + (i + 1) + " is invalid JSON."); }
      if (!validObject(item) || typeof item.id !== "string" || !item.id) {
        throw new Error(label + " line " + (i + 1) + " must be an object with a stable string id.");
      }
      if (seen.has(item.id)) throw new Error(label + " contains duplicate id " + item.id + ".");
      seen.add(item.id);
      rows.push(item);
    }
    return rows;
  }

  function nodeLabel(n) {
    const a = validObject(n.attributes) ? n.attributes : {};
    for (const k of ["title", "path", "qualname", "name", "external_id"]) {
      if (typeof a[k] === "string" && a[k]) return a[k];
    }
    return n.external_id || n.id;
  }
  function renderSearch() {
    const q = $("query").value.trim().toLocaleLowerCase();
    const matched = state.nodes.filter((n) => {
      const a = validObject(n.attributes) ? n.attributes : {};
      const hay = [n.id, n.kind, n.external_id, JSON.stringify(a)].join(" ").toLocaleLowerCase();
      return !q || hay.includes(q);
    }).slice(0, MAX_RESULTS);
    const connections = new Map();
    for (const e of state.edges) {
      for (const id of [e.source, e.target]) {
        if (typeof id === "string") connections.set(id, (connections.get(id) || 0) + 1);
      }
    }
    const body = $("results");
    clear(body);
    if (!matched.length) {
      const tr = el("tr"); const td = el("td", "", "No matching nodes.");
      td.colSpan = 4; tr.appendChild(td); body.appendChild(tr);
    } else {
      for (const n of matched) {
        const tr = el("tr");
        tr.appendChild(el("td", "", n.id));
        tr.appendChild(el("td", "", n.kind || "unknown"));
        const detail = validObject(n.attributes) ? (n.attributes.title || n.attributes.path || n.attributes.name || n.external_id || "") : (n.external_id || "");
        tr.appendChild(el("td", "", detail));
        tr.appendChild(el("td", "", connections.get(n.id) || 0));
        body.appendChild(tr);
      }
    }
    text("record-note", state.nodes.length.toLocaleString() + " nodes · " + state.edges.length.toLocaleString() + " edges loaded locally. Showing " + matched.length.toLocaleString() + " result(s), capped at " + MAX_RESULTS + ".");
  }

  async function readFile(input, label) {
    const file = input.files && input.files[0];
    if (!file) return null;
    if (file.size > 100 * 1024 * 1024) throw new Error(label + " exceeds the 100 MB safety limit.");
    return file.text();
  }
  async function loadPublished() {
    showError("");
    try {
      const response = await fetch("./data/snapshot.json", { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) throw new Error("No published projection at ./data/snapshot.json (HTTP " + response.status + "). Load a generated projection JSON file instead.");
      renderProjection(await response.json());
    } catch (error) {
      $("load-note").textContent = "Published snapshot unavailable. No fabricated values are displayed. " + error.message;
      $("load-note").className = "notice";
      showError(error.message);
    }
  }

  $("projection-file").addEventListener("change", async (event) => {
    try {
      showError("");
      const content = await readFile(event.target, "Projection");
      if (content === null) return;
      renderProjection(JSON.parse(content));
    } catch (error) { showError(error.message); }
  });
  $("node-file").addEventListener("change", async (event) => {
    try {
      showError("");
      const content = await readFile(event.target, "Node artifact");
      if (content === null) return;
      state.nodes = parseJsonl(content, "Nodes");
      state.nodeIds = new Set(state.nodes.map((n) => n.id));
      renderSearch();
    } catch (error) { showError(error.message); }
  });
  $("edge-file").addEventListener("change", async (event) => {
    try {
      showError("");
      const content = await readFile(event.target, "Edge artifact");
      if (content === null) return;
      state.edges = parseJsonl(content, "Edges");
      state.edgeIds = new Set(state.edges.map((e) => e.id));
      renderSearch();
    } catch (error) { showError(error.message); }
  });
  $("search-button").addEventListener("click", renderSearch);
  $("query").addEventListener("keydown", (event) => { if (event.key === "Enter") renderSearch(); });
  $("reload").addEventListener("click", loadPublished);
  loadPublished();
})();