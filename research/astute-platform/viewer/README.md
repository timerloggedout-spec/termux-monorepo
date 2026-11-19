# Interactive Research Astute Viewer

Serve the repository root over HTTP:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/research/astute-platform/viewer/`.

The viewer loads the experiment registry, renders typed graph instances, overlays selected alternate paths, compares shared and divergent nodes/edges, inspects node provenance, and restores view state from the URL fragment.

Interactions are read-only projections. Research edits flow through versioned files and the repository review workflow. The graph data table provides a keyboard- and screen-reader-friendly fallback.
