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
  if (fs.existsSync(RESULT)) return;

  // Wait for the orchestrator GO flag (solution staged).
  for (let i = 0; i < 300; i++) {
    if (fs.existsSync(GO)) break;
    await sleep(2000);
  }
  if (!fs.existsSync(GO)) {
    fs.writeFileSync(RESULT, JSON.stringify({ ok: false, detail: 'GO flag timeout' }));
    return;
  }

  const cr = vscode.extensions.getExtension('coderoad.coderoad');
  if (!cr) {
    fs.writeFileSync(RESULT, JSON.stringify({ ok: false, detail: 'coderoad extension not found' }));
    return;
  }
  if (!cr.isActive) { try { await cr.activate(); } catch (e) { /* continue */ } }
  await sleep(5000);

  let attempts = 0;
  let ok = false;
  let lastRaw = '';
  while (attempts < 5 && !ok) {
    attempts++;
    try {
      await vscode.commands.executeCommand('coderoad.run_test', { callbacks: { onSuccess: () => {} } });
    } catch (e) { /* runner may still be going; observe session */ }
    // Observe session state for up to ~40s per attempt.
    for (let i = 0; i < 20 && !ok; i++) {
      await sleep(2000);
      lastRaw = readSession();
      if (sessionShowsComplete(lastRaw)) ok = true;
    }
  }

  fs.writeFileSync(RESULT, JSON.stringify({
    ok,
    attempts,
    detail: ok ? 'session state shows step complete' : 'no completion marker in session state',
    session_tail: (lastRaw || readSession()).slice(-2000),
  }));
}

module.exports = { activate, deactivate: () => {} };
