// CodeRoad headless driver (fleet certifications leg).
// Contract (from coderoad/coderoad-vscode source):
//  - The CodeRoad extension auto-loads the tutorial from env
//    CODEROAD_TUTORIAL_URL on startup and runs its setup hooks machine-side.
//  - `coderoad.run_test` is a registered command that runs the current
//    step's tests through CodeRoad's own test runner; on pass the machine
//    marks the position complete and, at the final step, fires the
//    tutorial_complete webhook with the CODEROAD_WEBHOOK_TOKEN header.
// This driver only triggers that command once the orchestrator has staged
// the solution (GO flag) and observes CodeRoad's session-state file.
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const EV = process.env.CODEROAD_DRIVER_EVIDENCE || '/evidence';
const SESSION = process.env.CODEROAD_SESSION_STORAGE_PATH || '';
const GO = path.join(EV, 'GO');
const RESULT = path.join(EV, 'RESULT.json');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function phaseLog(msg) {
  try {
    fs.appendFileSync(path.join(EV, 'driver.log'),
      `${new Date().toISOString()} ${msg}\n`);
  } catch (e) { /* evidence fs is best-effort */ }
}

function readSession() {
  for (const p of SESSION_CANDIDATES) {
    try {
      if (p && fs.existsSync(p) && fs.statSync(p).isFile()) {
        const raw = fs.readFileSync(p, 'utf8');
        if (raw) return raw;
      }
    } catch (e) { /* ignore */ }
  }
  return '';
}

// CodeRoad keeps its machine state in the workspace memento DB
// (state.vscdb, SQLite). The JSON values sit in plain text inside it:
// keys "coderoad:currentTutorial" and "coderoad:position" (B10/B11).
function readPositionRaw() {
  try {
    if (!CTX || !CTX.storageUri) return '';
    const db = path.join(path.dirname(CTX.storageUri.fsPath), 'state.vscdb');
    if (!fs.existsSync(db)) return '';
    const buf = fs.readFileSync(db);
    const text = buf.toString('latin1');
    const i = text.indexOf('coderoad:position');
    if (i < 0) return '';
    return text.slice(i, i + 1200);
  } catch (e) { return ''; }
}

function positionShowsComplete(raw) {
  if (!raw) return false;
  const flat = raw.replace(/\\/g, '');
  return /"complete"\s*:\s*true/.test(flat);
}

let SESSION_CANDIDATES = [];
let CTX = null;
function buildSessionCandidates(context) {
  const out = [];
  if (SESSION) out.push(SESSION);
  try {
    const gsParent = path.dirname(context.globalStorageUri.fsPath);
    const crDir = path.join(gsParent, 'coderoad.coderoad');
    const walk = (d, depth) => {
      if (depth > 2 || !fs.existsSync(d)) return;
      for (const name of fs.readdirSync(d)) {
        const p = path.join(d, name);
        try {
          if (fs.statSync(p).isDirectory()) walk(p, depth + 1);
          else if (/\.json$/i.test(name)) out.push(p);
        } catch (e) { /* ignore */ }
      }
    };
    walk(crDir, 0);
  } catch (e) { /* ignore */ }
  try {
    const folders = vscode.workspace.workspaceFolders || [];
    for (const f of folders) {
      const crDir = path.join(f.uri.fsPath, '.coderoad');
      if (fs.existsSync(crDir)) {
        for (const name of fs.readdirSync(crDir)) {
          const p = path.join(crDir, name);
          if (fs.statSync(p).isFile()) out.push(p);
        }
      }
    }
  } catch (e) { /* ignore */ }
  return out;
}

// Completion evidence in the session state: the final step marked complete.
// Session shape is CodeRoad-internal; run 1 calibrates this detector, and the
// raw snapshot is always included in RESULT for that calibration.
function sessionShowsComplete(raw) {
  if (!raw) return false;
  return /"complete"\s*:\s*true/.test(raw) && /tutorial/i.test(raw);
}

async function activate(context) {
  try { fs.mkdirSync(EV, { recursive: true }); } catch (e) { /* exists */ }
  phaseLog(`activate() entered; EV=${EV} SESSION=${SESSION || '(unset)'}`);
  if (fs.existsSync(RESULT)) { phaseLog('RESULT pre-exists; driver exits'); return; }
  try {
    CTX = context;
    SESSION_CANDIDATES = buildSessionCandidates(context);
    phaseLog(`session candidates: ${SESSION_CANDIDATES.join(' | ') || '(none)'}`);
    await run();
  } catch (e) {
    phaseLog(`run() threw: ${e && e.stack ? e.stack : e}`);
    try {
      fs.writeFileSync(RESULT, JSON.stringify({ ok: false, detail: `driver exception: ${e}` }));
    } catch (e2) { /* ignore */ }
  }
}

async function run() {
  // Wait for the orchestrator GO flag (solution staged).
  for (let i = 0; i < 300; i++) {
    if (fs.existsSync(GO)) break;
    await sleep(2000);
  }
  if (!fs.existsSync(GO)) {
    phaseLog('GO flag timeout');
    fs.writeFileSync(RESULT, JSON.stringify({ ok: false, detail: 'GO flag timeout' }));
    return;
  }
  phaseLog('GO observed');

  const cr = vscode.extensions.getExtension('coderoad.coderoad');
  phaseLog(`getExtension(coderoad.coderoad) -> ${cr ? `found (active=${cr.isActive})` : 'NOT FOUND'}`);
  phaseLog(`all extension ids: ${vscode.extensions.all.map((x) => x.id).join(', ')}`);
  if (!cr) {
    fs.writeFileSync(RESULT, JSON.stringify({ ok: false, detail: 'coderoad extension not found' }));
    return;
  }
  if (!cr.isActive) { try { await cr.activate(); } catch (e) { phaseLog(`cr.activate() threw: ${e}`); } }
  phaseLog(`coderoad active=${cr.isActive}`);
  await sleep(5000);

  // Command surface + tutorial start: run_test on a cold session threw
  // TypeError inside CodeRoad (B6) — start the tutorial machine first.
  try {
    const cmds = (await vscode.commands.getCommands(true)).filter((c) => /coderoad/i.test(c));
    phaseLog(`coderoad commands: ${cmds.join(', ')}`);
  } catch (e) { phaseLog(`getCommands threw: ${e}`); }
  try {
    await vscode.commands.executeCommand('coderoad.start');
    phaseLog('coderoad.start returned');
  } catch (e) { phaseLog(`coderoad.start threw: ${e}`); }
  await sleep(8000);
  if (CTX) {
    SESSION_CANDIDATES = buildSessionCandidates(CTX);
    phaseLog(`session candidates after start: ${SESSION_CANDIDATES.join(' | ') || '(none)'}`);
  }
  phaseLog(`session after start: len=${readSession().length}`);

  let attempts = 0;
  let ok = false;
  let lastRaw = '';
  while (attempts < 5 && !ok) {
    attempts++;
    try {
      if (attempts % 2 === 1) {
        await vscode.commands.executeCommand('coderoad.run_test', { callbacks: { onSuccess: () => {} } });
      } else {
        await vscode.commands.executeCommand('coderoad.run_test');
      }
      phaseLog(`run_test attempt ${attempts} returned`);
    } catch (e) { phaseLog(`run_test attempt ${attempts} threw: ${e}`); }
    // Observe session state for up to ~40s per attempt.
    for (let i = 0; i < 20 && !ok; i++) {
      await sleep(2000);
      lastRaw = readSession();
      if (sessionShowsComplete(lastRaw)) ok = true;
      const pos = readPositionRaw();
      if (pos) {
        lastRaw = pos;
        if (positionShowsComplete(pos)) ok = true;
        if (i === 0) phaseLog(`position after attempt ${attempts}: ${pos.slice(0, 400)}`);
      }
    }
    phaseLog(`attempt ${attempts} observed: complete=${ok} session_len=${lastRaw.length}`);
  }

  fs.writeFileSync(RESULT, JSON.stringify({
    ok,
    attempts,
    detail: ok ? 'session state shows step complete' : 'no completion marker in session state',
    session_tail: (lastRaw || readSession()).slice(-2000),
  }));
}

module.exports = { activate, deactivate: () => {} };
