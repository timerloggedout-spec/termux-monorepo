(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const state = { catalog: null, selected: null, sourceVisible: false, scale: 1, x: 0, y: 0, drag: null };
  const kindLabels = { document: "MD", mermaid: "MMD", svg: "SVG", png: "PNG" };
  const kindNames = { document: "Markdown document", mermaid: "Mermaid diagram", svg: "Imported SVG", png: "PNG preview" };
  const rootUrl = "https://github.com/timerloggedout-spec/termux-monorepo";
  const tree = $("tree");

  function announce(message) { $("live-status").textContent = message || ""; }
  function formatBytes(value) {
    if (value < 1024) return value + " B";
    if (value < 1048576) return (value / 1024).toFixed(1) + " KB";
    return (value / 1048576).toFixed(2) + " MB";
  }
  function catalogUrl(path) { return new URL(path, document.baseURI).href; }
  function addFolder(node, label) {
    if (!node.folders.has(label)) node.folders.set(label, { folders: new Map(), files: [] });
    return node.folders.get(label);
  }
  function buildNested(items) {
    const root = { folders: new Map(), files: [] };
    for (const item of items) {
      const parts = item.path.split("/");
      let node = root;
      for (const part of parts.slice(0, -1)) node = addFolder(node, part);
      node.files.push(item);
    }
    return root;
  }
  function renderNested(node, parent, depth, queryActive) {
    for (const [name, child] of [...node.folders.entries()].sort((a,b) => a[0].localeCompare(b[0]))) {
      const details = document.createElement("details");
      details.open = queryActive;
      const summary = document.createElement("summary");
      summary.textContent = name;
      details.append(summary);
      const inner = document.createElement("div");
      inner.className = "tree-folder";
      renderNested(child, inner, depth + 1, queryActive);
      details.append(inner);
      parent.append(details);
    }
    for (const item of node.files.sort((a,b) => a.title.localeCompare(b.title))) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "tree-item";
      button.dataset.id = item.id;
      button.setAttribute("aria-current", state.selected?.id === item.id ? "page" : "false");
      const label = document.createElement("span");
      label.className = "file-label";
      label.textContent = item.title;
      const tag = document.createElement("span");
      tag.className = "kind-tag";
      tag.textContent = kindLabels[item.kind] || item.kind.toUpperCase();
      button.append(label, tag);
      button.addEventListener("click", () => {
        selectItem(item);
        if (window.matchMedia("(max-width: 760px)").matches) closeSidebar();
      });
      parent.append(button);
    }
  }
  function renderTree() {
    const query = $("search").value.trim().toLowerCase();
    const kind = $("kind-filter").value;
    const items = state.catalog.items.filter(item => {
      const matchesKind = kind === "all" || item.kind === kind;
      const haystack = [item.title, item.path, item.summary, item.category].join(" ").toLowerCase();
      return matchesKind && (!query || haystack.includes(query));
    });
    tree.replaceChildren();
    if (!items.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No sources match this search.";
      tree.append(empty);
      return;
    }
    const categories = new Map();
    for (const item of items) {
      if (!categories.has(item.category)) categories.set(item.category, []);
      categories.get(item.category).push(item);
    }
    for (const [category, group] of [...categories.entries()].sort((a,b) => a[0].localeCompare(b[0]))) {
      const details = document.createElement("details");
      const containsSelected = group.some(item => item.id === state.selected?.id);
      details.open = Boolean(query) || containsSelected;
      const summary = document.createElement("summary");
      summary.textContent = category;
      details.append(summary);
      const nested = document.createElement("div");
      nested.className = "tree-folder";
      renderNested(buildNested(group), nested, 0, Boolean(query) || containsSelected);
      details.append(nested);
      tree.append(details);
    }
  }
  function setStats() {
    const c = state.catalog;
    $("metric-docs").textContent = c.document_count;
    $("metric-mermaid").textContent = c.diagram_count;
    $("metric-svg").textContent = c.svg_count;
    $("metric-total").textContent = c.item_count;
    $("catalog-sha").textContent = c.source_sha;
    $("catalog-ref").textContent = c.source_ref;
    $("catalog-time").textContent = c.generated_at;
    $("catalog-schema").textContent = "v" + c.schema_version;
    $("build-state").textContent = "Catalog built from " + c.source_ref + " · " + c.source_sha.slice(0, 10);
  }
  function setProvenance(item) {
    $("prov-path").textContent = item.path;
    $("prov-hash").textContent = item.sha256;
    $("prov-ref").textContent = item.source_ref;
    $("prov-size").textContent = formatBytes(item.bytes);
    $("prov-built").textContent = state.catalog.generated_at;
    $("prov-link").href = item.source_url;
    $("prov-link").textContent = "Open canonical file ↗";
    $("provenance-ref").textContent = item.source_ref;
  }
  function resetTransform() {
    state.scale = 1; state.x = 0; state.y = 0;
    applyTransform();
  }
  function applyTransform() {
    $("diagram-canvas").style.transform = "translate(" + state.x + "px," + state.y + "px) scale(" + state.scale + ")";
    $("zoom-level").textContent = Math.round(state.scale * 100) + "%";
  }
  function setScale(value) {
    state.scale = Math.max(.35, Math.min(3.5, value));
    applyTransform();
  }
  function setViewerMode(mode) {
    state.sourceVisible = mode === "source";
    $("diagram-stage").hidden = state.sourceVisible;
    $("source-view").hidden = !state.sourceVisible;
    $("show-rendered").classList.toggle("active", !state.sourceVisible);
    $("show-source").classList.toggle("active", state.sourceVisible);
  }
  async function fetchText(path) {
    const response = await fetch(catalogUrl(path), { cache: "no-cache" });
    if (!response.ok) throw new Error("Unable to load " + path + " (" + response.status + ")");
    return response.text();
  }
  function rewriteMarkdownLinks(container, item) {
    for (const link of container.querySelectorAll("a[href]")) {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || /^(https?:|mailto:|tel:)/i.test(href)) {
        if (/^https?:/i.test(href || "")) { link.target = "_blank"; link.rel = "noopener noreferrer"; }
        continue;
      }
      const resolved = new URL(href, "https://repo.local/" + item.path);
      const repoPath = decodeURIComponent(resolved.pathname.replace(/^\\/+/, ""));
      const related = state.catalog.items.find(candidate => candidate.path === repoPath);
      if (related) {
        link.href = "#source-" + encodeURIComponent(related.id);
        link.addEventListener("click", event => {
          event.preventDefault();
          selectItem(related);
        });
      } else {
        link.href = new URL(href, rootUrl + "/blob/" + item.source_ref + "/" + item.path).href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
    }
    for (const img of container.querySelectorAll("img[src]")) {
      const src = img.getAttribute("src");
      if (src && !/^(https?:|data:)/i.test(src)) {
        img.src = new URL(src, "https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/" + item.source_ref + "/" + item.path).href;
      }
      img.loading = "lazy";
    }
  }
  async function showDocument(item) {
    $("document-view").hidden = false;
    $("diagram-view").hidden = true;
    $("viewer-toolbar").hidden = true;
    const source = await fetchText(item.site_path);
    const target = $("document-view");
    if (window.marked && window.DOMPurify) {
      const rendered = window.marked.parse(source, { gfm: true, breaks: false });
      target.innerHTML = window.DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } });
      rewriteMarkdownLinks(target, item);
    } else {
      const pre = document.createElement("pre");
      pre.textContent = source;
      target.replaceChildren(pre);
      announce("Markdown renderer unavailable; showing the canonical source text.");
    }
  }
  async function showDiagram(item) {
    $("document-view").hidden = true;
    $("diagram-view").hidden = false;
    $("viewer-toolbar").hidden = false;
    $("diagram-stage").hidden = false;
    $("source-view").hidden = true;
    $("show-rendered").classList.add("active");
    $("show-source").classList.remove("active");
    state.sourceVisible = false;
    const imagePath = item.kind === "mermaid" ? item.render_path : item.asset_path;
    $("diagram-image").src = catalogUrl(imagePath);
    $("diagram-image").alt = item.title + " — " + kindNames[item.kind];
    $("show-source").hidden = item.kind === "png";
    $("show-rendered").textContent = item.kind === "png" ? "Preview" : "Rendered";
    $("diagram-caption").textContent = item.kind === "mermaid"
      ? "Generated SVG from the canonical Mermaid source. Open Source to inspect the editable .mmd file."
      : "Imported visual asset. The original file remains available from its canonical repository path.";
    $("diagram-image").onerror = () => announce("The visual asset could not be loaded: " + imagePath);
    resetTransform();
  }
  async function showSource(item) {
    const sourcePath = item.site_path || item.asset_path;
    const text = await fetchText(sourcePath);
    $("source-code").textContent = text;
    setViewerMode("source");
  }
  async function selectItem(item) {
    state.selected = item;
    renderTree();
    $("selected-category").textContent = item.category;
    $("selected-title").textContent = item.title;
    $("selected-summary").textContent = item.summary;
    $("selected-kind").textContent = kindNames[item.kind] || item.kind;
    setProvenance(item);
    announce("Loading " + item.path);
    try {
      if (item.kind === "document") await showDocument(item);
      else await showDiagram(item);
      announce("Loaded " + item.path);
    } catch (error) {
      $("document-view").hidden = false;
      $("diagram-view").hidden = true;
      $("viewer-toolbar").hidden = true;
      $("document-view").textContent = error.message;
      announce(error.message);
    }
  }
  function closeSidebar() {
    $("sidebar").classList.remove("open");
    $("sidebar-scrim").classList.remove("open");
    $("nav-toggle").setAttribute("aria-expanded", "false");
  }
  function openSidebar() {
    $("sidebar").classList.add("open");
    $("sidebar-scrim").classList.add("open");
    $("nav-toggle").setAttribute("aria-expanded", "true");
  }
  async function init() {
    try {
      const response = await fetch(catalogUrl("./catalog.json"), { cache: "no-cache" });
      if (!response.ok) throw new Error("Architecture catalog unavailable (" + response.status + ")");
      state.catalog = await response.json();
      setStats();
      renderTree();
      const preferred = state.catalog.items.find(item => item.path === "architecture.md") || state.catalog.items[0];
      if (preferred) await selectItem(preferred);
    } catch (error) {
      $("build-state").textContent = "Catalog unavailable";
      tree.textContent = error.message;
      announce(error.message);
    }
  }
  $("search").addEventListener("input", renderTree);
  $("kind-filter").addEventListener("change", renderTree);
  $("expand-all").addEventListener("click", () => {
    const details = [...tree.querySelectorAll("details")];
    const expand = details.some(node => !node.open);
    details.forEach(node => { node.open = expand; });
    $("expand-all").textContent = expand ? "Collapse all" : "Expand all";
  });
  $("nav-toggle").addEventListener("click", openSidebar);
  $("close-sidebar").addEventListener("click", closeSidebar);
  $("sidebar-scrim").addEventListener("click", closeSidebar);
  $("zoom-in").addEventListener("click", () => setScale(state.scale + .15));
  $("zoom-out").addEventListener("click", () => setScale(state.scale - .15));
  $("fit-view").addEventListener("click", resetTransform);
  $("show-rendered").addEventListener("click", () => setViewerMode("rendered"));
  $("show-source").addEventListener("click", () => {
    if (!state.selected) return;
    showSource(state.selected).catch(error => announce(error.message));
  });
  $("fullscreen").addEventListener("click", () => {
    const stage = $("diagram-stage");
    if (stage.requestFullscreen) stage.requestFullscreen().catch(error => announce(error.message));
  });
  const canvas = $("diagram-canvas");
  canvas.addEventListener("pointerdown", event => {
    if (state.sourceVisible) return;
    state.drag = { x: event.clientX - state.x, y: event.clientY - state.y, pointerId: event.pointerId };
    canvas.classList.add("dragging");
    canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener("pointermove", event => {
    if (!state.drag || state.drag.pointerId !== event.pointerId) return;
    state.x = event.clientX - state.drag.x;
    state.y = event.clientY - state.drag.y;
    applyTransform();
  });
  const stopDrag = event => {
    if (state.drag && state.drag.pointerId === event.pointerId) {
      state.drag = null;
      canvas.classList.remove("dragging");
    }
  };
  canvas.addEventListener("pointerup", stopDrag);
  canvas.addEventListener("pointercancel", stopDrag);
  $("diagram-stage").addEventListener("wheel", event => {
    if ($("diagram-view").hidden || state.sourceVisible) return;
    event.preventDefault();
    setScale(state.scale + (event.deltaY < 0 ? .08 : -.08));
  }, { passive: false });
  init();
})();
