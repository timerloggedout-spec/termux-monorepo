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

function parsePosition() {
  const raw = readPositionRaw();
  if (!raw) return null;
  const flat = raw.replace(/\\/g, '');
  const lv = /"levelId"\s*:\s*"([^"]+)"/.exec(flat);
  const st = /"stepId"\s*:\s*"([^"]+)"/.exec(flat);
  const cp = /"complete"\s*:\s*(true|false)/.exec(flat);
  if (!lv && !st) return null;
  return {
    levelId: lv ? lv[1] : null,
    stepId: st ? st[1] : null,
    complete: cp ? cp[1] === 'true' : false,
  };
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

  // Workshop mode (driver v4): step-loop replay of a manifest through a
  // real interactive bash (the camper shell contract: HISTFILE at the
  // workspace parent, course .bashrc prompt hooks maintain test/.cwd and
  // test/.next_command), one run_test per step, position-gated.
  const manifestPath = process.env.CODEROAD_MANIFEST_PATH || '';
  if (manifestPath && fs.existsSync(manifestPath)) {
    await runWorkshop(manifestPath);
    return;
  }

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

async function runWorkshop(manifestPath) {
  const man = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const steps = man.steps || [];
  const folder = (vscode.workspace.workspaceFolders || [])[0];
  const wsPath = folder ? folder.uri.fsPath : '/workspace/project';
  const parent = path.dirname(wsPath);
  phaseLog(`workshop loop: ${steps.length} steps, ws=${wsPath}`);

  // The course setup (run by coderoad.start) installs the camper .bashrc;
  // wait until its prompt hooks are in place before spawning the shell.
  const bashrc = path.join(process.env.HOME || '', '.bashrc');
  for (let i = 0; i < 30; i++) {
    try {
      if (fs.readFileSync(bashrc, 'utf8').includes('PROMPT_COMMAND')) break;
    } catch (e) { /* not yet */ }
    await sleep(2000);
  }
  const { spawn } = require('child_process');
  const shell = spawn('bash', ['-i'], {
    cwd: wsPath,
    env: { ...process.env, TERM: 'dumb', HISTFILE: path.join(parent, '.bash_history') },
  });
  shell.stdout.on('data', (d) => phaseLog(`shell-out: ${String(d).slice(0, 160)}`));
  shell.stderr.on('data', (d) => phaseLog(`shell-err: ${String(d).slice(0, 160)}`));
  shell.on('exit', (c) => phaseLog(`shell exited rc=${c}`));
  const send = async (cmd, settle) => {
    try { shell.stdin.write(cmd + '\n'); } catch (e) { phaseLog(`send failed: ${e}`); }
    await sleep(settle || 900);
  };
  await sleep(2500);

  let completed = 0;
  const failures = [];
  let consec = 0;
  const deadline = Date.now() + 50 * 60 * 1000;
  for (let idx = 0; idx < steps.length; idx++) {
    if (Date.now() > deadline) { failures.push('deadline'); break; }
    const entry = steps[idx];
    // Sync gate: act only once CodeRoad's position sits at this step.
    let synced = false;
    for (let i = 0; i < 25 && !synced; i++) {
      const pos = parsePosition();
      if (pos && pos.levelId === entry.level) synced = true;
      else await sleep(1200);
    }
    if (!synced) {
      failures.push(`${entry.step}:sync`);
      phaseLog(`step ${entry.step}: position never synced; aborting loop`);
      break;
    }
    let advanced = false;
    for (let attempt = 1; attempt <= 3 && !advanced; attempt++) {
      const cmds = (attempt >= 2 && entry.cd_first)
        ? [entry.cd_first, ...(entry.commands || [])]
        : (entry.commands || []);
      for (const c of cmds) {
        phaseLog(`step ${entry.step} attempt ${attempt}: $ ${c}`);
        await send(c, 900);
      }
      await sleep(1200);
      try {
        await vscode.commands.executeCommand('coderoad.run_test');
        phaseLog(`step ${entry.step} run_test attempt ${attempt} returned`);
      } catch (e) { phaseLog(`step ${entry.step} run_test threw: ${e}`); }
      // A passed step stays AT its position with complete=true (the
      // runner sets {...position, complete: true}); navigation is a
      // separate set_current_position call (the webview's continue).
      for (let i = 0; i < 20 && !advanced; i++) {
        await sleep(1200);
        const pos = parsePosition();
        if (pos && pos.levelId === entry.level && pos.complete) advanced = true;
      }
    }
    if (advanced && idx < steps.length - 1) {
      const nxt = steps[idx + 1];
      try {
        await vscode.commands.executeCommand('coderoad.set_current_position',
          { levelId: nxt.level, stepId: nxt.step, complete: false });
        phaseLog(`position -> ${nxt.step}`);
      } catch (e) { phaseLog(`set_current_position threw: ${e}`); }
      await sleep(800);
    }
    if (advanced) {
      completed++;
      consec = 0;
      phaseLog(`step ${entry.step} ADVANCED (${completed}/${steps.length})`);
    } else {
      failures.push(entry.step);
      consec++;
      phaseLog(`step ${entry.step} STALLED (${consec} consecutive)`);
      if (consec >= 3) { phaseLog('3 consecutive stalls; aborting loop'); break; }
    }
  }
  const pos = parsePosition();
  const lastLevel = steps.length ? steps[steps.length - 1].level : null;
  const ok = completed === steps.length ||
    !!(pos && pos.complete && pos.levelId === lastLevel);
  try { shell.stdin.write('exit\n'); } catch (e) { /* gone */ }
  try { shell.kill(); } catch (e) { /* gone */ }
  fs.writeFileSync(RESULT, JSON.stringify({
    ok,
    mode: 'workshop-loop',
    steps_total: steps.length,
    steps_completed: completed,
    failures,
    detail: ok ? 'all steps advanced; final position complete'
      : `loop ended: ${completed}/${steps.length} advanced`,
    session_tail: readPositionRaw().slice(-1200),
  }));
  phaseLog(`workshop loop done: ok=${ok} completed=${completed}/${steps.length} failures=${failures.join(',')}`);
}

module.exports = { activate, deactivate: () => {} };
