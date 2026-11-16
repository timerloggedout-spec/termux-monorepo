import React, { useMemo, useState } from "react";
import { recombiningTrellis, strictTree } from "./markov-engine.mjs";

const states = ["Idle", "Scan", "Process", "Sync"];
const transitions = {
  Idle: { Scan: 0.7, Process: 0.3 },
  Scan: { Scan: 0.2, Process: 0.6, Sync: 0.2 },
  Process: { Process: 0.4, Sync: 0.6 },
  Sync: { Sync: 1 }
};
const initial = { Idle: 1, Scan: 0, Process: 0, Sync: 0 };

export default function ArchWizMarkovTrellis({ horizon = 4 }) {
  const [mode, setMode] = useState("trellis");
  const [selected, setSelected] = useState(null);
  const layers = useMemo(
    () => mode === "trellis"
      ? recombiningTrellis({ states, transitions, initial, horizon })
      : strictTree({ states, transitions, initial, horizon }),
    [mode, horizon]
  );

  const maxRows = Math.max(...layers.map((layer) => layer.nodes.length));
  const nodePosition = (node, layer) => ({
    x: 80 + (node.time / Math.max(1, horizon)) * 720,
    y: 40 + ((layer.nodes.indexOf(node) + 1) / (layer.nodes.length + 1)) * 300
  });

  return (
    <section style={{ background: "#03070d", color: "#00e5ff", padding: 16, fontFamily: "monospace" }}>
      <header style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <strong style={{ color: "#ffb700" }}>ARCHW1Z.MARKOV.LAB</strong>
        <span>MODE: {mode.toUpperCase()}</span>
      </header>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <button onClick={() => setMode("tree")}>UNFOLDED TREE</button>
        <button onClick={() => setMode("trellis")}>RECOMBINING TRELLIS</button>
      </div>
      <svg viewBox="0 0 800 360" width="100%" role="img" aria-label="Markov state trellis">
        {layers.flatMap((layer) => layer.nodes).map((node) => {
          const layer = layers[node.time];
          const p = nodePosition(node, layer);
          return (
            <g key={node.id} onClick={() => setSelected(node.id)} style={{ cursor: "pointer" }}>
              {(node.incoming || []).map((edge) => {
                const parent = layers[node.time - 1]?.nodes.find((n) => n.id === edge.from);
                if (!parent) return null;
                const q = nodePosition(parent, layers[parent.time]);
                return <line key={edge.from} x1={q.x} y1={q.y} x2={p.x} y2={p.y}
                  stroke="#00e5ff" strokeOpacity={0.25} strokeWidth={Math.max(1, edge.probability * 7)} />;
              })}
              <circle cx={p.x} cy={p.y} r={selected === node.id ? 20 : 15}
                fill="#091824" stroke={node.state === "Sync" ? "#ffb700" : "#00e5ff"} strokeWidth={selected === node.id ? 3 : 1.5} />
              <text x={p.x} y={p.y + 31} fill="#fff" textAnchor="middle" fontSize="9">{node.state}</text>
              <text x={p.x} y={p.y - 23} fill="#00ff66" textAnchor="middle" fontSize="8">P={node.probability.toFixed(3)}</text>
            </g>
          );
        })}
      </svg>
      <footer style={{ borderTop: "1px solid #0a2336", paddingTop: 8, fontSize: 11 }}>
        selected={selected || "none"} · layers={layers.length} · maxRows={maxRows}
      </footer>
    </section>
  );
}
