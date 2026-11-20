import { useState, useEffect, useRef, useCallback } from "react";

// ─── ARBITRAGE ENGINE ───────────────────────────────────────────────
const TOKENS = ["ETH", "BTC", "SOL", "BNB", "ARB", "MATIC", "AVAX", "LINK"];
const EXCHANGES = ["Binance", "OKX", "Uniswap", "Coinbase", "Bybit", "Kraken", "Curve", "dYdX"];

function buildLogGraph(injectProfit = false) {
  const g = {};
  TOKENS.forEach(a => {
    g[a] = {};
    TOKENS.forEach(b => {
      if (a === b) return;
      const deviation = (Math.random() - 0.495) * 0.025;
      g[a][b] = -Math.log(1 + deviation); // negative log → profit detection
    });
  });
  if (injectProfit) {
    const profit = Math.random() * 9 + 0.4;
    const p = profit / 3;
    const tokens = TOKENS.slice().sort(() => Math.random() - 0.5);
    const [a, b, c] = tokens;
    g[a][b] = -Math.log(1 + p / 100);
    g[b][c] = -Math.log(1 + p / 100);
    g[c][a] = -Math.log(1 + p / 100 + 0.0005);
  }
  return g;
}

function bellmanFord(graph) {
  const nodes = Object.keys(graph);
  const dist = Object.fromEntries(nodes.map(n => [n, 0]));
  const prev = Object.fromEntries(nodes.map(n => [n, null]));

  for (let i = 0; i < nodes.length - 1; i++) {
    nodes.forEach(u => {
      Object.entries(graph[u] || {}).forEach(([v, w]) => {
        if (dist[u] + w < dist[v]) {
          dist[v] = dist[u] + w;
          prev[v] = u;
        }
      });
    });
  }

  const cycles = [];
  nodes.forEach(u => {
    Object.entries(graph[u] || {}).forEach(([v, w]) => {
      if (dist[u] + w < dist[v] - 1e-10) {
        const path = [v];
        let cur = u;
        const seen = new Set();
        while (cur && cur !== v && !seen.has(cur)) {
          seen.add(cur);
          path.unshift(cur);
          cur = prev[cur];
        }
        path.push(path[0]);
        if (path.length >= 4) {
          let tw = 0;
          for (let i = 0; i < path.length - 1; i++) {
            tw += graph[path[i]]?.[path[i + 1]] ?? 0;
          }
          const pct = (1 - Math.exp(tw)) * 100;
          if (pct > 0.01 && pct < 10000) {
            cycles.push({
              path,
              profitPct: pct,
              exchange: EXCHANGES[Math.floor(Math.random() * EXCHANGES.length)],
              timestamp: Date.now(),
              tier: pct > 5 ? "JACKPOT" : pct > 2 ? "HIGH" : pct > 0.5 ? "MED" : "LOW",
            });
          }
        }
      }
    });
  });

  return cycles.sort((a, b) => b.profitPct - a.profitPct);
}

// ─── TECH TREE DATA ─────────────────────────────────────────────────
const TECH_TIERS = [
  {
    name: "MICRO-CAP INITIALIZER", levels: "1–3", color: "#00ff88", icon: "🌱",
    features: ["Manual arbitrage scanning", "3-hop Bellman-Ford", "Q-Bucks reward system", "Max bet: $2,000", "Core Scanner Init"],
    manaReq: 0,
  },
  {
    name: "NANO-CAP INTEGRATOR", levels: "4–6", color: "#00d4ff", icon: "⚡",
    features: ["Bellman-Ford Engine", "Smart Batching (edge conflicts)", "5-hop depth scanning", "Max bet: $13,000", "Inter-Exchange Unlock"],
    manaReq: 4,
  },
  {
    name: "ULTRA LOW OPERATOR", levels: "7–9", color: "#ffd700", icon: "🔥",
    features: ["Pump.fun launcher", "All intra-exchange slots", "Temporal Arbitrage", "10-hop depth scanning", "Femto price tier"],
    manaReq: 7,
  },
  {
    name: "QUANTUM SWARM MASTER", levels: "10–12+", color: "#ff006e", icon: "👑",
    features: ["No betting limits", "Private Strategy Rooms", "Encrypted P2P Collaboration", "Swarm Equilibrium Protocol", "Planck price tier"],
    manaReq: 10,
  },
];

const PRICE_TIERS = [
  { name: "MICRO CAP", threshold: "< $0.001", color: "#00d4ff", icon: "💧", label: "BLUE/DRIP" },
  { name: "PICO", threshold: "< $1E-9", color: "#ff006e", icon: "🔥", label: "NEON PINK/FIRE" },
  { name: "PLANCK", threshold: "< $1E-15", color: "#ffd700", icon: "⭐", label: "GOLD/STAR" },
];

const SLOT_SYMBOLS = ["ETH", "BTC", "SOL", "💎", "7️⃣", "ARB", "BNB", "⭐"];

// ─── HELPERS ────────────────────────────────────────────────────────
const glow = (c, s = 20) => `0 0 ${s}px ${c}66`;
const textGlow = (c) => ({ color: c, textShadow: `0 0 8px ${c}, 0 0 16px ${c}88` });
const panelStyle = (c) => ({
  background: `${c}0d`,
  border: `1px solid ${c}44`,
  boxShadow: `0 0 24px ${c}18, inset 0 0 40px ${c}06`,
  borderRadius: 14,
  padding: 20,
});

function Reel({ symbol, spinning }) {
  return (
    <div style={{
      width: 76, height: 76, display: "flex", alignItems: "center", justifyContent: "center",
      background: "radial-gradient(circle, #0d0025 60%, #000)",
      border: "2px solid #ff006e66",
      borderRadius: 10,
      fontSize: symbol.length <= 3 ? 22 : 18,
      fontWeight: "bold",
      color: "#00d4ff",
      textShadow: `0 0 12px #00d4ff`,
      boxShadow: spinning ? "0 0 20px #ff006e44, inset 0 0 10px #ff006e22" : "0 0 6px #00d4ff22",
      transition: "all 0.06s",
      fontFamily: "'Courier New', monospace",
      letterSpacing: symbol.length > 3 ? 0 : 1,
      animation: spinning ? "reelSpin 0.08s infinite alternate" : "none",
    }}>
      {symbol}
    </div>
  );
}

// ─── MAIN COMPONENT ─────────────────────────────────────────────────
export default function QuanTMFOAM() {
  const [tab, setTab] = useState("casino");
  const [bankroll, setBankroll] = useState(10000);
  const [betSize, setBetSize] = useState(200);
  const [level, setLevel] = useState(1);
  const [xp, setXp] = useState(0);
  const [mana, setMana] = useState(47);
  const [qBucks, setQBucks] = useState(12);
  const [reels, setReels] = useState(["ETH", "BTC", "SOL"]);
  const [spinning, setSpinning] = useState(false);
  const [jackpot, setJackpot] = useState(false);
  const [jackpotMsg, setJackpotMsg] = useState("");
  const [activeOpp, setActiveOpp] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [scanLog, setScanLog] = useState([]);
  const [pnl, setPnl] = useState(0);
  const [pnlHistory, setPnlHistory] = useState(Array(30).fill(0));
  const [totalTrades, setTotalTrades] = useState(0);
  const [wins, setWins] = useState(0);
  const [autoScan, setAutoScan] = useState(false);
  const [particles, setParticles] = useState([]);
  const [hopDepth, setHopDepth] = useState(3);
  const [scanMode, setScanMode] = useState("intra");
  const [swarmNodes, setSwarmNodes] = useState(() =>
    Array.from({ length: 10 }, (_, i) => ({
      id: i,
      x: 15 + Math.random() * 70,
      y: 15 + Math.random() * 70,
      type: ["SCAN", "RELAY", "VAULT"][i % 3],
      active: true,
      pulse: Math.random(),
    }))
  );

  const autoRef = useRef(null);
  const particleKey = useRef(0);

  const triggerParticles = useCallback(() => {
    const ps = Array.from({ length: 28 }, (_, i) => ({
      id: particleKey.current++,
      x: 30 + Math.random() * 40,
      y: 20 + Math.random() * 60,
      dx: (Math.random() - 0.5) * 300,
      dy: -(Math.random() * 300 + 50),
      color: ["#ff006e", "#ffd700", "#00d4ff", "#00ff88"][Math.floor(Math.random() * 4)],
      size: Math.random() * 8 + 4,
    }));
    setParticles(ps);
    setTimeout(() => setParticles([]), 2200);
  }, []);

  const executeScan = useCallback(() => {
    if (spinning || bankroll < betSize) return;
    setSpinning(true);
    setJackpot(false);
    setActiveOpp(null);

    let ticks = 0;
    const total = 14 + Math.floor(Math.random() * 8);
    const spinInt = setInterval(() => {
      setReels([
        SLOT_SYMBOLS[Math.floor(Math.random() * SLOT_SYMBOLS.length)],
        SLOT_SYMBOLS[Math.floor(Math.random() * SLOT_SYMBOLS.length)],
        SLOT_SYMBOLS[Math.floor(Math.random() * SLOT_SYMBOLS.length)],
      ]);
      ticks++;
      if (ticks >= total) {
        clearInterval(spinInt);
        const hasOpp = Math.random() < 0.38;
        const graph = buildLogGraph(hasOpp);
        const cycles = bellmanFord(graph);
        const valid = cycles.filter(c => c.profitPct < 10000);
        const ts = new Date().toLocaleTimeString();

        if (valid.length > 0) {
          const best = valid[0];
          const isJackpot = best.profitPct > 5;
          const profit = (best.profitPct / 100) * betSize;
          const finalReels = best.path.filter(t => TOKENS.includes(t)).slice(0, 3);
          if (finalReels.length === 3) setReels(finalReels);
          else setReels(["ETH", best.path[1] || "BTC", "SOL"]);

          setBankroll(b => b + profit);
          setPnl(p => p + profit);
          setPnlHistory(h => [...h.slice(1), (h[h.length - 1] ?? 0) + profit]);
          setMana(m => Math.min(m + 3, 100));
          setQBucks(q => q + Math.max(1, Math.floor(profit / 8)));
          setXp(x => x + 10 + (isJackpot ? 20 : 0));
          setWins(w => w + 1);
          setActiveOpp(best);
          setOpportunities(prev => [best, ...prev.slice(0, 11)]);
          setScanLog(prev => [
            { text: `[${ts}] ✅ ${best.path.join("→")} | +${best.profitPct.toFixed(4)}% | $+${profit.toFixed(3)} | ${best.exchange}`, ok: true },
            ...prev.slice(0, 19),
          ]);
          if (isJackpot) {
            setJackpot(true);
            setJackpotMsg(`💎 JACKPOT! +${best.profitPct.toFixed(2)}% | $${profit.toFixed(2)}`);
            triggerParticles();
          }
        } else {
          const fee = betSize * 0.0008;
          setBankroll(b => Math.max(0, b - fee));
          setPnl(p => p - fee);
          setPnlHistory(h => [...h.slice(1), (h[h.length - 1] ?? 0) - fee]);
          setReels(["—", "—", "—"]);
          setScanLog(prev => [
            { text: `[${ts}] ❌ No cycle detected | -$${fee.toFixed(4)} scan fee`, ok: false },
            ...prev.slice(0, 19),
          ]);
        }

        setTotalTrades(t => {
          const next = t + 1;
          if (next % 12 === 0) setLevel(l => Math.min(l + 1, 12));
          return next;
        });
        setSpinning(false);
      }
    }, 75);
  }, [spinning, bankroll, betSize, triggerParticles]);

  useEffect(() => {
    if (autoScan) {
      autoRef.current = setInterval(executeScan, 2200);
    } else {
      clearInterval(autoRef.current);
    }
    return () => clearInterval(autoRef.current);
  }, [autoScan, executeScan]);

  // Swarm node heartbeat
  useEffect(() => {
    const iv = setInterval(() => {
      setSwarmNodes(ns =>
        ns.map(n => ({
          ...n,
          active: Math.random() > 0.15,
          pulse: Math.random(),
        }))
      );
    }, 1400);
    return () => clearInterval(iv);
  }, []);

  const winRate = totalTrades > 0 ? Math.round((wins / totalTrades) * 100) : 0;
  const levelPct = Math.min(100, (xp % 120) / 1.2);
  const levelName = level <= 3 ? "Micro-Cap Init" : level <= 6 ? "Nano-Cap Int" : level <= 9 ? "Ultra Low Op" : "Quantum Swarm Master";

  const nc = { scan: "#00d4ff", relay: "#ff006e", vault: "#ffd700" };

  return (
    <div style={{
      minHeight: "100vh",
      background: "radial-gradient(ellipse at 20% 50%, #120025 0%, #050510 40%, #000208 100%)",
      fontFamily: "'Courier New', Courier, monospace",
      color: "#d0d8ff",
      overflow: "hidden",
      position: "relative",
    }}>
      {/* CSS */}
      <style>{`
        @keyframes reelSpin { from { transform: scaleY(1.08); } to { transform: scaleY(0.94); } }
        @keyframes pulseGlow { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }
        @keyframes jackpotFlash { 0%,100% { box-shadow: 0 0 30px #ffd70099; } 50% { box-shadow: 0 0 60px #ffd700ff, 0 0 100px #ff006e88; } }
        @keyframes scanLine { 0% { top: -4px; } 100% { top: 100%; } }
        @keyframes particle { 0% { transform: translate(0,0) scale(1); opacity: 1; } 100% { transform: translate(var(--dx), var(--dy)) scale(0); opacity: 0; } }
        @keyframes nodebeat { 0%,100% { transform: scale(1); } 50% { transform: scale(1.4); } }
        @keyframes gradientShift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #ff006e44; border-radius: 2px; }
        button:active { transform: scale(0.97); }
      `}</style>

      {/* Scanlines */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 900,
        background: "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,212,255,0.012) 3px,rgba(0,212,255,0.012) 4px)",
      }} />
      <div style={{
        position: "fixed", left: 0, right: 0, height: 2, background: "linear-gradient(90deg,transparent,#00d4ff66,transparent)",
        animation: "scanLine 5s linear infinite", pointerEvents: "none", zIndex: 901,
      }} />

      {/* Particles */}
      {particles.map(p => (
        <div key={p.id} style={{
          position: "fixed", left: `${p.x}%`, top: `${p.y}%`,
          width: p.size, height: p.size, borderRadius: "50%",
          background: p.color, boxShadow: `0 0 8px ${p.color}`,
          pointerEvents: "none", zIndex: 999,
          "--dx": `${p.dx}px`, "--dy": `${p.dy}px`,
          animation: `particle 1.8s ease-out forwards`,
        }} />
      ))}

      {/* HEADER */}
      <div style={{
        padding: "14px 24px",
        background: "linear-gradient(90deg, #0d0025ee, #18003aee, #0d0025ee)",
        borderBottom: "1px solid #ff006e33",
        backdropFilter: "blur(10px)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 50,
      }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 0 }}>
          <span style={{ ...textGlow("#ff006e"), fontSize: 22, fontWeight: 900, letterSpacing: 3 }}>QUAN</span>
          <span style={{ ...textGlow("#00d4ff"), fontSize: 22, fontWeight: 900, letterSpacing: 3 }}>TM</span>
          <span style={{ color: "#ffffff44", margin: "0 10px", fontSize: 18 }}>|</span>
          <span style={{ color: "#888", fontSize: 13, letterSpacing: 2 }}>FOAM HFT SWARM v12</span>
        </div>
        <div style={{ display: "flex", gap: 20, fontSize: 13, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "#ffd700" }}>⚡</span>
            <span style={{ color: "#ffd700", fontWeight: "bold" }}>{mana}</span>
            <span style={{ color: "#555", fontSize: 10 }}>MANA</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "#ff006e" }}>◆</span>
            <span style={{ color: "#ff006e", fontWeight: "bold" }}>{qBucks}</span>
            <span style={{ color: "#555", fontSize: 10 }}>Q-BUCKS</span>
          </div>
          <div style={{
            padding: "4px 12px", borderRadius: 20,
            background: "#ff006e22", border: "1px solid #ff006e44",
            ...textGlow("#ff006e"), fontSize: 13, fontWeight: "bold",
          }}>
            LVL {level}
          </div>
          <div style={{ color: pnl >= 0 ? "#00ff88" : "#ff4444", fontWeight: "bold" }}>
            {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)}
          </div>
        </div>
      </div>

      {/* NAV */}
      <div style={{
        display: "flex", background: "#06001a",
        borderBottom: "1px solid #ffffff0d",
      }}>
        {[
          { id: "casino", icon: "🎰", label: "CASINO", c: "#ff006e" },
          { id: "engine", icon: "⚙️", label: "ENGINE", c: "#00d4ff" },
          { id: "techtree", icon: "🌳", label: "TECH TREE", c: "#ffd700" },
          { id: "swarm", icon: "🕸️", label: "SWARM", c: "#00ff88" },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            flex: 1, padding: "13px 8px", border: "none", cursor: "pointer",
            background: tab === t.id ? `${t.c}15` : "transparent",
            borderBottom: `2px solid ${tab === t.id ? t.c : "transparent"}`,
            color: tab === t.id ? t.c : "#444",
            fontSize: 13, fontFamily: "inherit", fontWeight: 700, letterSpacing: 1,
            textShadow: tab === t.id ? `0 0 10px ${t.c}` : "none",
            transition: "all 0.2s",
          }}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div style={{ padding: "20px 24px", maxWidth: 1400, margin: "0 auto" }}>

        {/* ── CASINO TAB ── */}
        {tab === "casino" && (
          <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>

            {/* SLOT MACHINE */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{
                ...panelStyle("#ff006e"),
                animation: jackpot ? "jackpotFlash 0.4s infinite" : "none",
              }}>
                <div style={{ textAlign: "center", marginBottom: 16 }}>
                  <div style={{ ...textGlow("#ff006e"), fontSize: 16, fontWeight: 900, letterSpacing: 4, marginBottom: 2 }}>
                    ⚡ QUANTUM SLOTS ⚡
                  </div>
                  <div style={{ color: "#555", fontSize: 10, letterSpacing: 2 }}>ARBITRAGE DETECTION ENGINE</div>
                </div>

                {/* Reels */}
                <div style={{
                  display: "flex", justifyContent: "center", gap: 10, padding: 16,
                  background: "#000", borderRadius: 12,
                  border: `2px solid ${jackpot ? "#ffd700" : "#ff006e44"}`,
                  marginBottom: 14,
                }}>
                  {reels.map((s, i) => <Reel key={i} symbol={s} spinning={spinning} />)}
                </div>

                {jackpot && (
                  <div style={{
                    textAlign: "center", marginBottom: 12,
                    ...textGlow("#ffd700"), fontSize: 18, fontWeight: 900,
                    animation: "pulseGlow 0.6s infinite",
                    letterSpacing: 2,
                  }}>
                    {jackpotMsg}
                  </div>
                )}

                {activeOpp && !jackpot && (
                  <div style={{ ...panelStyle("#00ff88"), padding: 12, marginBottom: 12, fontSize: 12, animation: "fadeIn 0.3s ease" }}>
                    <div style={{ color: "#00ff88", fontWeight: "bold", marginBottom: 4 }}>✅ NEGATIVE CYCLE FOUND</div>
                    <div style={{ color: "#aaa", marginBottom: 2 }}>Path: {activeOpp.path.join(" → ")}</div>
                    <div style={{ ...textGlow("#00ff88"), fontSize: 17, fontWeight: "bold" }}>
                      +{activeOpp.profitPct.toFixed(4)}%
                    </div>
                    <div style={{ color: "#444", fontSize: 10 }}>{activeOpp.exchange} · {activeOpp.tier}</div>
                  </div>
                )}

                {/* Bet slider */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 12 }}>
                    <span style={{ color: "#666" }}>BET SIZE</span>
                    <span style={{ color: "#ffd700", fontWeight: "bold" }}>${betSize.toLocaleString()}</span>
                  </div>
                  <input type="range" min={1} max={Math.min(bankroll, 5000)} value={betSize}
                    onChange={e => setBetSize(Number(e.target.value))}
                    style={{ width: "100%", accentColor: "#ff006e", cursor: "pointer" }}
                  />
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#333", marginTop: 2 }}>
                    <span>$1</span><span>$5K</span>
                  </div>
                </div>

                {/* Bankroll display */}
                <div style={{
                  display: "flex", justifyContent: "space-between", padding: "10px 14px",
                  background: "#ffffff07", borderRadius: 8, marginBottom: 14, fontSize: 13,
                }}>
                  <span style={{ color: "#555" }}>BANKROLL</span>
                  <span style={{ color: bankroll >= 10000 ? "#00ff88" : bankroll > 5000 ? "#ffd700" : "#ff4444", fontWeight: "bold" }}>
                    ${bankroll.toFixed(2)}
                  </span>
                </div>

                {/* Action buttons */}
                <div style={{ display: "flex", gap: 10 }}>
                  <button onClick={executeScan} disabled={spinning || bankroll < betSize} style={{
                    flex: 2, padding: "15px 0", borderRadius: 10, border: "none",
                    background: spinning ? "#1a1a2e" : "linear-gradient(135deg, #ff006e, #cc0055)",
                    color: spinning ? "#444" : "#fff",
                    fontSize: 15, fontWeight: 900, cursor: spinning ? "not-allowed" : "pointer",
                    boxShadow: spinning ? "none" : `0 0 20px #ff006e55, 0 4px 15px #ff006e33`,
                    letterSpacing: 1, fontFamily: "inherit",
                    transition: "all 0.15s",
                  }}>
                    {spinning ? "⟳ SCANNING..." : "🎰  PULL LEVER"}
                  </button>
                  <button onClick={() => setAutoScan(a => !a)} style={{
                    flex: 1, padding: "15px 0", borderRadius: 10, border: "none",
                    background: autoScan ? "linear-gradient(135deg,#ff4444,#aa0000)" : "linear-gradient(135deg,#005eff,#003baa)",
                    color: "#fff", fontSize: 12, fontWeight: 900,
                    cursor: "pointer", fontFamily: "inherit",
                    boxShadow: autoScan ? "0 0 16px #ff444455" : "0 0 16px #005eff44",
                    transition: "all 0.15s",
                  }}>
                    {autoScan ? "⏹ STOP" : "▶ AUTO"}
                  </button>
                </div>
              </div>

              {/* Price Tier Matrix */}
              <div style={{ ...panelStyle("#00d4ff") }}>
                <div style={{ ...textGlow("#00d4ff"), fontSize: 11, letterSpacing: 2, marginBottom: 14 }}>
                  ◆ PRICE TIER MATRIX
                </div>
                {PRICE_TIERS.map(tier => (
                  <div key={tier.name} style={{
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                    padding: "8px 10px", marginBottom: 6, borderRadius: 8,
                    background: `${tier.color}0d`, border: `1px solid ${tier.color}33`,
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 16 }}>{tier.icon}</span>
                      <span style={{ color: tier.color, fontSize: 12, fontWeight: "bold" }}>{tier.name}</span>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ color: "#666", fontSize: 10 }}>{tier.threshold}</div>
                      <div style={{ color: tier.color, fontSize: 9, letterSpacing: 1 }}>{tier.label}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* RIGHT PANEL */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Stats grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                {[
                  { label: "TRADES", val: totalTrades, c: "#00d4ff" },
                  { label: "WIN RATE", val: `${winRate}%`, c: wins >= totalTrades * 0.5 ? "#00ff88" : "#ff4444" },
                  { label: "NET P/L", val: `${pnl >= 0 ? "+" : ""}$${Math.abs(pnl).toFixed(2)}`, c: pnl >= 0 ? "#00ff88" : "#ff4444" },
                  { label: "BANKROLL", val: `$${bankroll.toFixed(0)}`, c: bankroll >= 10000 ? "#ffd700" : bankroll > 7000 ? "#aaa" : "#ff4444" },
                ].map(s => (
                  <div key={s.label} style={{
                    ...panelStyle(s.c), textAlign: "center", padding: 16,
                  }}>
                    <div style={{ color: "#444", fontSize: 9, letterSpacing: 2, marginBottom: 6 }}>{s.label}</div>
                    <div style={{ ...textGlow(s.c), fontSize: 20, fontWeight: 900 }}>{s.val}</div>
                  </div>
                ))}
              </div>

              {/* P/L Chart */}
              <div style={{ ...panelStyle("#00d4ff") }}>
                <div style={{ color: "#00d4ff", fontSize: 11, letterSpacing: 2, marginBottom: 12 }}>
                  📈 REAL-TIME P/L TRACKER
                </div>
                <div style={{
                  height: 90, display: "flex", alignItems: "flex-end", gap: 2,
                  background: "#000", padding: 10, borderRadius: 8,
                }}>
                  {pnlHistory.map((v, i, arr) => {
                    const mn = Math.min(...arr), mx = Math.max(...arr);
                    const range = Math.max(mx - mn, 0.01);
                    const h = ((v - mn) / range) * 70 + 8;
                    const c = v >= 0 ? "#00ff88" : "#ff4444";
                    return (
                      <div key={i} style={{
                        flex: 1, height: `${h}%`, background: c,
                        opacity: 0.4 + (i / arr.length) * 0.6,
                        borderRadius: "2px 2px 0 0",
                        boxShadow: `0 0 4px ${c}`,
                        minHeight: 2,
                        transition: "height 0.3s ease",
                      }} />
                    );
                  })}
                </div>
              </div>

              {/* Opportunities feed */}
              <div style={{ ...panelStyle("#ffd700"), flex: 1 }}>
                <div style={{ ...textGlow("#ffd700"), fontSize: 11, letterSpacing: 2, marginBottom: 12 }}>
                  ⚡ LIVE ARBITRAGE PATHS
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 240, overflowY: "auto" }}>
                  {opportunities.length === 0 ? (
                    <div style={{ color: "#333", textAlign: "center", padding: 30, fontSize: 13 }}>
                      Pull lever to begin scanning...
                    </div>
                  ) : opportunities.map((opp, i) => (
                    <div key={i} style={{
                      display: "flex", alignItems: "center", justifyContent: "space-between",
                      padding: "8px 12px", borderRadius: 8,
                      background: i === 0 ? "#ffd70011" : "#ffffff07",
                      border: `1px solid ${i === 0 ? "#ffd70033" : "#ffffff0a"}`,
                      fontSize: 12, animation: i === 0 ? "fadeIn 0.3s ease" : "none",
                    }}>
                      <div>
                        <span style={{ color: "#666", fontSize: 10 }}>{opp.exchange}</span>
                        <div style={{ color: "#ccc", fontSize: 11, marginTop: 2 }}>
                          {opp.path?.join(" → ")}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{
                          color: opp.profitPct > 5 ? "#ffd700" : opp.profitPct > 2 ? "#00ff88" : "#00d4ff",
                          fontWeight: "bold", fontSize: 14,
                        }}>
                          +{opp.profitPct.toFixed(4)}%
                        </div>
                        <div style={{ fontSize: 9, color: "#444", marginTop: 2 }}>{opp.tier}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── ENGINE TAB ── */}
        {tab === "engine" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>

            {/* Left: Algorithm Panel */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ ...panelStyle("#00d4ff") }}>
                <div style={{ ...textGlow("#00d4ff"), fontSize: 14, letterSpacing: 3, marginBottom: 18 }}>
                  ⚙️ HFT ENGINE
                </div>

                {/* Exchanges */}
                <div style={{ marginBottom: 18 }}>
                  <div style={{ color: "#444", fontSize: 10, letterSpacing: 2, marginBottom: 10 }}>
                    ACTIVE EXCHANGES (30+)
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {EXCHANGES.map(ex => (
                      <div key={ex} style={{
                        padding: "4px 10px", borderRadius: 20, fontSize: 11,
                        background: "#00d4ff15", border: "1px solid #00d4ff33",
                        color: "#00d4ff",
                      }}>{ex}</div>
                    ))}
                  </div>
                </div>

                {/* Hop depth */}
                <div style={{ marginBottom: 18 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: 12 }}>
                    <span style={{ color: "#666" }}>HOP DEPTH (Bellman-Ford)</span>
                    <span style={{ color: "#ffd700", fontWeight: "bold" }}>{hopDepth} hops</span>
                  </div>
                  <input type="range" min={3} max={level >= 7 ? 10 : level >= 4 ? 7 : 3}
                    value={hopDepth} onChange={e => setHopDepth(Number(e.target.value))}
                    style={{ width: "100%", accentColor: "#00d4ff", cursor: "pointer" }}
                  />
                  {hopDepth > 5 && (
                    <div style={{ color: "#ffd70099", fontSize: 10, marginTop: 4 }}>
                      ⚠ Deep scan — Nano-Cap+ required
                    </div>
                  )}
                </div>

                {/* Scan mode */}
                <div style={{ marginBottom: 18 }}>
                  <div style={{ color: "#444", fontSize: 10, letterSpacing: 2, marginBottom: 10 }}>SCAN MODE</div>
                  <div style={{ display: "flex", gap: 10 }}>
                    {["intra", "inter"].map(mode => (
                      <button key={mode} onClick={() => setScanMode(mode)} style={{
                        flex: 1, padding: "10px 0", borderRadius: 8, border: "none", cursor: "pointer",
                        background: scanMode === mode ? "#00d4ff22" : "#ffffff08",
                        color: scanMode === mode ? "#00d4ff" : "#444",
                        border: `1px solid ${scanMode === mode ? "#00d4ff55" : "#ffffff11"}`,
                        fontSize: 12, fontFamily: "inherit", fontWeight: "bold",
                        transition: "all 0.2s",
                        boxShadow: scanMode === mode ? "0 0 12px #00d4ff33" : "none",
                      }}>
                        {mode === "intra" ? "🏛️ INTRA" : "🔗 INTER"}
                      </button>
                    ))}
                  </div>
                  <div style={{ color: "#444", fontSize: 10, marginTop: 8 }}>
                    {scanMode === "intra"
                      ? "Single exchange — no withdrawal delays. Default mode."
                      : "Cross-venue hunting — larger spreads, higher risk."}
                  </div>
                </div>

                {/* Algo display */}
                <div style={{
                  background: "#000", borderRadius: 10, padding: 16,
                  border: "1px solid #00d4ff22", fontFamily: "monospace", fontSize: 11, lineHeight: 1.7,
                }}>
                  <div style={{ color: "#00d4ff44", marginBottom: 4 }}>// bellman_ford.py — negative cycle detection</div>
                  <div style={{ color: "#555" }}>{"dist = {v: 0 for v in nodes}"}</div>
                  <div style={{ color: "#555" }}>for i in range(|V|-1):</div>
                  <div style={{ paddingLeft: 16, color: "#555" }}>for u,v,w in edges:</div>
                  <div style={{ paddingLeft: 32, color: "#aaa" }}>if dist[u]+w &lt; dist[v]:</div>
                  <div style={{ paddingLeft: 48, color: "#ffd700" }}>relax(v)</div>
                  <div style={{ color: "#555", marginTop: 4 }}>for u,v,w in edges:</div>
                  <div style={{ paddingLeft: 16, color: "#aaa" }}>if dist[u]+w &lt; dist[v]:</div>
                  <div style={{ paddingLeft: 32, color: "#ff006e", fontWeight: "bold" }}>yield ARBITRAGE_CYCLE(path)</div>
                </div>
              </div>

              {/* Rate sanitization */}
              <div style={{ ...panelStyle("#00ff88") }}>
                <div style={{ ...textGlow("#00ff88"), fontSize: 12, letterSpacing: 2, marginBottom: 12 }}>
                  🛡️ RATE SANITIZATION & INVERSION
                </div>
                <div style={{ color: "#888", fontSize: 12, lineHeight: 1.7 }}>
                  Profit outliers above <span style={{ color: "#ff4444" }}>10,000%</span> are automatically flagged as suspicious jackpots and rejected. Floor price logic (<span style={{ color: "#00ff88" }}>realPrice</span>) is applied to ensure real-world profitability before execution.
                </div>
                <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                  {["Outlier Filter", "Floor Price", "Gas Estimation"].map(tag => (
                    <div key={tag} style={{
                      padding: "4px 10px", borderRadius: 20, fontSize: 10,
                      background: "#00ff8815", border: "1px solid #00ff8833", color: "#00ff88",
                    }}>{tag}</div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: Scan Log */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ ...panelStyle("#ffd700"), flex: 1 }}>
                <div style={{ ...textGlow("#ffd700"), fontSize: 12, letterSpacing: 2, marginBottom: 14 }}>
                  📡 LIVE SCAN LOG
                </div>
                <div style={{
                  height: 340, overflowY: "auto", background: "#000",
                  borderRadius: 10, padding: 14,
                  border: "1px solid #ffd70022",
                  fontFamily: "monospace", fontSize: 11,
                }}>
                  {scanLog.length === 0 ? (
                    <div style={{ color: "#222", textAlign: "center", paddingTop: 40 }}>
                      Awaiting scan execution...
                    </div>
                  ) : scanLog.map((entry, i) => (
                    <div key={i} style={{
                      color: entry.ok ? "#00ff88" : "#ff4444",
                      marginBottom: 5, paddingBottom: 5,
                      borderBottom: "1px solid #ffffff07",
                      opacity: Math.max(0.2, 1 - i * 0.04),
                      animation: i === 0 ? "fadeIn 0.2s ease" : "none",
                    }}>
                      {entry.text}
                    </div>
                  ))}
                </div>
              </div>

              {/* Scanner version */}
              <div style={{ ...panelStyle("#ff006e") }}>
                <div style={{ ...textGlow("#ff006e"), fontSize: 11, letterSpacing: 2, marginBottom: 12 }}>
                  🔄 SCANNER EVOLUTION
                </div>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                    <thead>
                      <tr>
                        {["Feature", "V10", "V12"].map(h => (
                          <th key={h} style={{ color: h === "V12" ? "#ff006e" : "#666", padding: "6px 12px", textAlign: "left", borderBottom: "1px solid #ffffff11", fontSize: 10, letterSpacing: 1 }}>
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        ["Exchange Count", "4 Exchanges", "30+ Exchanges"],
                        ["Arb Mode", "Inter-Exchange Only", "Default Intra-Exchange"],
                        ["Price Tiers", "Micro Cap Only", "Pico, Femto & Planck"],
                        ["Hop Depth", "3 hops", "Up to 10 hops"],
                        ["Algorithm", "Brute Force", "Bellman-Ford"],
                      ].map(([feat, v10, v12]) => (
                        <tr key={feat}>
                          <td style={{ padding: "7px 12px", color: "#666", borderBottom: "1px solid #ffffff07" }}>{feat}</td>
                          <td style={{ padding: "7px 12px", color: "#444", borderBottom: "1px solid #ffffff07" }}>{v10}</td>
                          <td style={{ padding: "7px 12px", color: "#ff006e", borderBottom: "1px solid #ffffff07", fontWeight: "bold" }}>{v12}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── TECH TREE TAB ── */}
        {tab === "techtree" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

            {/* Level progress */}
            <div style={{ ...panelStyle("#ffd700") }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <div>
                  <div style={{ ...textGlow("#ffd700"), fontSize: 22, fontWeight: 900 }}>LEVEL {level}</div>
                  <div style={{ color: "#888", fontSize: 12, marginTop: 2 }}>{levelName}</div>
                </div>
                <div style={{ display: "flex", gap: 24 }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ ...textGlow("#ffd700"), fontSize: 22, fontWeight: 900 }}>{mana}</div>
                    <div style={{ color: "#555", fontSize: 10, letterSpacing: 1 }}>MANA</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ ...textGlow("#ff006e"), fontSize: 22, fontWeight: 900 }}>{qBucks}</div>
                    <div style={{ color: "#555", fontSize: 10, letterSpacing: 1 }}>Q-BUCKS</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ ...textGlow("#00d4ff"), fontSize: 22, fontWeight: 900 }}>{totalTrades}</div>
                    <div style={{ color: "#555", fontSize: 10, letterSpacing: 1 }}>TRADES</div>
                  </div>
                </div>
              </div>
              <div style={{ background: "#000", borderRadius: 8, height: 12, overflow: "hidden" }}>
                <div style={{
                  height: "100%", width: `${levelPct}%`,
                  background: "linear-gradient(90deg, #ff006e, #ffd700, #00ff88)",
                  backgroundSize: "200% 100%",
                  animation: "gradientShift 3s ease infinite",
                  boxShadow: "0 0 12px #ffd700",
                  transition: "width 0.5s ease",
                }} />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 10, color: "#333" }}>
                <span>LVL 1</span><span>LVL 12</span>
              </div>
            </div>

            {/* Tier cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
              {TECH_TIERS.map((tier) => {
                const unlocked = level >= tier.manaReq;
                return (
                  <div key={tier.name} style={{
                    ...panelStyle(unlocked ? tier.color : "#333"),
                    opacity: unlocked ? 1 : 0.55,
                    position: "relative", overflow: "hidden",
                  }}>
                    {!unlocked && (
                      <div style={{
                        position: "absolute", inset: 0, display: "flex", alignItems: "center",
                        justifyContent: "center", background: "#000000bb", borderRadius: 14,
                        fontSize: 44, zIndex: 10,
                      }}>
                        🔒
                      </div>
                    )}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                      <div>
                        <span style={{ fontSize: 22, marginRight: 8 }}>{tier.icon}</span>
                        <div style={{ ...textGlow(tier.color), fontSize: 13, fontWeight: 900, letterSpacing: 1, marginTop: 4 }}>
                          {tier.name}
                        </div>
                        <div style={{ color: "#555", fontSize: 10, marginTop: 2 }}>Levels {tier.levels}</div>
                      </div>
                      <div style={{
                        padding: "4px 12px", borderRadius: 20, fontSize: 10, fontWeight: "bold",
                        background: unlocked ? tier.color : "#333",
                        color: unlocked ? "#000" : "#666",
                        boxShadow: unlocked ? `0 0 10px ${tier.color}` : "none",
                      }}>
                        {unlocked ? "UNLOCKED" : "LOCKED"}
                      </div>
                    </div>
                    {tier.features.map(f => (
                      <div key={f} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7, fontSize: 12 }}>
                        <span style={{ color: tier.color, fontSize: 10 }}>▶</span>
                        <span style={{ color: unlocked ? "#bbb" : "#444" }}>{f}</span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>

            {/* Mana System */}
            <div style={{ ...panelStyle("#ff006e") }}>
              <div style={{ ...textGlow("#ff006e"), fontSize: 13, letterSpacing: 3, marginBottom: 18 }}>
                ⚡ MANA SYSTEM: POWERING THE SWARM
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
                {[
                  { title: "COMPUTE MANA GENERATION", desc: "Earn +3 Mana for pulling the Drag Lever. +3 for every successful scan execution to maintain node health.", color: "#00d4ff" },
                  { title: "DATA & TRADE MANA", desc: "Earn +1 Mana for API fetches and relays. +10 for Bot Executions to incentivize liquidity provision to the swarm.", color: "#ffd700" },
                  { title: "MANA SUSTAINABILITY (LVL 12)", desc: "The Level 12 Swarm Equilibrium background rebalancer consumes -2 Compute Mana per cycle, forcing nodes to maintain Passive Extraction.", color: "#ff006e" },
                ].map(m => (
                  <div key={m.title} style={{ ...panelStyle(m.color), padding: 16 }}>
                    <div style={{ ...textGlow(m.color), fontSize: 11, fontWeight: 900, marginBottom: 10, letterSpacing: 1 }}>
                      {m.title}
                    </div>
                    <div style={{ color: "#777", fontSize: 11, lineHeight: 1.6 }}>{m.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── SWARM TAB ── */}
        {tab === "swarm" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>

            {/* Network graph */}
            <div style={{ ...panelStyle("#00ff88") }}>
              <div style={{ ...textGlow("#00ff88"), fontSize: 14, letterSpacing: 3, marginBottom: 14 }}>
                🕸️ P2P SWARM NETWORK
              </div>
              <div style={{
                position: "relative", height: 280, background: "#000",
                borderRadius: 12, overflow: "hidden",
                border: "1px solid #00ff8822",
              }}>
                <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
                  {swarmNodes.map((n1, i) =>
                    swarmNodes.slice(i + 1).map(n2 => (
                      <line key={`${n1.id}-${n2.id}`}
                        x1={`${n1.x}%`} y1={`${n1.y}%`}
                        x2={`${n2.x}%`} y2={`${n2.y}%`}
                        stroke={n1.active && n2.active ? "#00ff8830" : "#ffffff08"}
                        strokeWidth={n1.active && n2.active ? 1.5 : 0.5}
                      />
                    ))
                  )}
                </svg>
                {swarmNodes.map(n => {
                  const c = { SCAN: "#00d4ff", RELAY: "#ff006e", VAULT: "#ffd700" }[n.type];
                  return (
                    <div key={n.id} title={n.type} style={{
                      position: "absolute",
                      left: `${n.x}%`, top: `${n.y}%`,
                      transform: "translate(-50%,-50%)",
                      width: 18, height: 18, borderRadius: "50%",
                      background: n.active ? c : "#1a1a2e",
                      boxShadow: n.active ? `0 0 14px ${c}, 0 0 28px ${c}55` : "none",
                      transition: "all 1.2s ease",
                      animation: n.active ? `nodebeat ${1.5 + n.pulse}s ease-in-out infinite` : "none",
                    }} />
                  );
                })}
                <div style={{
                  position: "absolute", bottom: 10, left: 12, right: 12,
                  display: "flex", gap: 12, fontSize: 10,
                }}>
                  {[["SCAN", "#00d4ff"], ["RELAY", "#ff006e"], ["VAULT", "#ffd700"]].map(([t, c]) => (
                    <div key={t} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <div style={{ width: 8, height: 8, borderRadius: "50%", background: c, boxShadow: `0 0 5px ${c}` }} />
                      <span style={{ color: c }}>{t}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, fontSize: 12 }}>
                <div>
                  <span style={{ color: "#555" }}>Active Nodes</span>
                  <span style={{ color: "#00ff88", fontWeight: "bold", marginLeft: 10 }}>
                    {swarmNodes.filter(n => n.active).length}/{swarmNodes.length}
                  </span>
                </div>
                <div>
                  <span style={{ color: "#555" }}>State Sync</span>
                  <span style={{ color: "#00d4ff", fontWeight: "bold", marginLeft: 10 }}>Yjs CRDT</span>
                </div>
                <div>
                  <span style={{ color: "#555" }}>Data</span>
                  <span style={{ color: "#ffd700", fontWeight: "bold", marginLeft: 10 }}>WebTorrent</span>
                </div>
              </div>
            </div>

            {/* Swarm stats */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ ...panelStyle("#00d4ff") }}>
                <div style={{ ...textGlow("#00d4ff"), fontSize: 12, letterSpacing: 2, marginBottom: 14 }}>
                  📊 SWARM INFRASTRUCTURE
                </div>
                {[
                  { k: "Consensus Algorithm", v: "RAFT / EPaxos", c: "#00d4ff" },
                  { k: "Sync Protocol", v: "Yjs (CRDT)", c: "#00ff88" },
                  { k: "Data Sharing", v: "WebTorrent P2P", c: "#ffd700" },
                  { k: "Node Type", v: "Browser Autonomous", c: "#ff006e" },
                  { k: "Network Level", v: `L${level} Access`, c: "#ff006e" },
                  { k: "Fingerprinting", v: "NPU/GPU + Jitter", c: "#00d4ff" },
                ].map(s => (
                  <div key={s.k} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "9px 0", borderBottom: "1px solid #ffffff0a", fontSize: 12,
                  }}>
                    <span style={{ color: "#555" }}>{s.k}</span>
                    <span style={{ color: s.c, fontWeight: "bold" }}>{s.v}</span>
                  </div>
                ))}
              </div>

              {/* Swarm Economy */}
              <div style={{ ...panelStyle("#ffd700") }}>
                <div style={{ ...textGlow("#ffd700"), fontSize: 12, letterSpacing: 2, marginBottom: 14 }}>
                  💰 SWARM ECONOMY
                </div>
                <div style={{ fontSize: 12, lineHeight: 1.8, color: "#777" }}>
                  <div style={{ marginBottom: 10 }}>
                    <span style={{ color: "#ffd700", fontWeight: "bold" }}>5% Mandatory Index:</span> Every winning trade routes 5% of profit to a shared Swarm Index Fund distributed among swarm members.
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <span style={{ color: "#00d4ff", fontWeight: "bold" }}>Wallet Proxy Authority:</span> Trade payloads are compressed and signed via a pre-configured proxy server to broadcast REST transactions.
                  </div>
                  <div>
                    <span style={{ color: "#ff006e", fontWeight: "bold" }}>Q-Bucks Rewards:</span> Primary denomination for on-chain nodes and real-data contributions.
                  </div>
                </div>
                <div style={{ marginTop: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#555", marginBottom: 6 }}>
                    <span>MANA GAUGE</span>
                    <span style={{ color: "#ffd700" }}>{mana}/100</span>
                  </div>
                  <div style={{ background: "#000", borderRadius: 6, height: 10, overflow: "hidden" }}>
                    <div style={{
                      height: "100%", width: `${mana}%`,
                      background: "linear-gradient(90deg, #ffd700, #ff006e)",
                      boxShadow: "0 0 8px #ffd700",
                      transition: "width 0.5s ease",
                    }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Hardware tier (full width) */}
            <div style={{ gridColumn: "1 / -1", ...panelStyle("#ff006e") }}>
              <div style={{ ...textGlow("#ff006e"), fontSize: 12, letterSpacing: 2, marginBottom: 16 }}>
                🖥️ HARDWARE TIER LIST — HFT SUITABILITY
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                {[
                  { tier: "Latest SoCs", sub: "Snapdragon 8 Gen, Apple A18", suit: "EXCELLENT", c: "#00ff88" },
                  { tier: "High-end ARM", sub: "Exynos 2200, GPU accel", suit: "GOOD", c: "#00d4ff" },
                  { tier: "Mid-range ARM", sub: "MediaTek Dimensity", suit: "MODERATE", c: "#ffd700" },
                  { tier: "Older ARM", sub: "Cortex-A55", suit: "LIMITED", c: "#ff8844" },
                  { tier: "Embedded DSPs", sub: "AI Accel offload only", suit: "AUXILIARY", c: "#666" },
                  { tier: "Legacy Mobile", sub: "ARM/M cores, minimal", suit: "MINIMAL", c: "#444" },
                ].map(h => (
                  <div key={h.tier} style={{
                    padding: "12px 16px", borderRadius: 10,
                    background: `${h.c}0d`, border: `1px solid ${h.c}33`,
                  }}>
                    <div style={{ color: h.c, fontWeight: "bold", fontSize: 13, marginBottom: 4 }}>{h.tier}</div>
                    <div style={{ color: "#555", fontSize: 11, marginBottom: 8 }}>{h.sub}</div>
                    <div style={{
                      display: "inline-block", padding: "3px 10px", borderRadius: 20,
                      background: `${h.c}22`, color: h.c, fontSize: 10, fontWeight: "bold",
                    }}>{h.suit}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: "12px 24px", marginTop: 20,
        borderTop: "1px solid #ffffff08",
        display: "flex", justifyContent: "space-between", alignItems: "center",
        fontSize: 10, color: "#333",
      }}>
        <span>QUANTM FOAM HFT SWARM v12 · BELLMAN-FORD ENGINE · LAYER A/B/C ARCHITECTURE</span>
        <span>SIMULATION ONLY · NO REAL FUNDS · EDUCATIONAL DEMO</span>
      </div>
    </div>
  );
}
