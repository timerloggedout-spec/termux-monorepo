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
  try {
    if (SESSION && fs.existsSync(SESSION)) return fs.readFileSync(SESSION, 'utf8');
  } catch (e) { /* ignore */ }
  return '';
}

// Completion evidence in the session state: the final step marked complete.
// Session shape is CodeRoad-internal; run 1 calibrates this detector, and the
// raw snapshot is always included in RESULT for that calibration.
function sessionShowsComplete(raw) {
  if (!raw) return false;
  return /"complete"\s*:\s*true/.test(raw) && /tutorial/i.test(raw);
}

async function activate() {
  try { fs.mkdirSync(EV, { recursive: true }); } catch (e) { /* exists */ }
  phaseLog(`activate() entered; EV=${EV} SESSION=${SESSION || '(unset)'}`);
  if (fs.existsSync(RESULT)) { phaseLog('RESULT pre-exists; driver exits'); return; }
  try {
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

  let attempts = 0;
  let ok = false;
  let lastRaw = '';
  while (attempts < 5 && !ok) {
    attempts++;
    try {
      await vscode.commands.executeCommand('coderoad.run_test', { callbacks: { onSuccess: () => {} } });
      phaseLog(`run_test attempt ${attempts} returned`);
    } catch (e) { phaseLog(`run_test attempt ${attempts} threw: ${e}`); }
    // Observe session state for up to ~40s per attempt.
    for (let i = 0; i < 20 && !ok; i++) {
      await sleep(2000);
      lastRaw = readSession();
      if (sessionShowsComplete(lastRaw)) ok = true;
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
