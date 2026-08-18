#!/usr/bin/env node
/**
 * Lightweight Termux browser-wrapper runner.
 *
 * It function-matches the safe common behavior of the repository's
 * reverse-engineering corpus: provider-owned profile reuse, manual login,
 * selector readiness checks, browser UI send, and normalized response text.
 * It intentionally never reads cookies, local storage, headers, request
 * bodies, response bodies, screenshots, or direct provider endpoints.
 */
import crypto from 'crypto';
import fs from 'fs';
import os from 'os';
import path from 'path';
import process from 'process';
import { createRequire } from 'module';
import { fileURLToPath, pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPOSITORY_ROOT = path.resolve(__dirname, '..', '..');
const DEFAULT_CHROMIUM = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEFAULT_ROOT = path.join(os.homedir(), '.multi-ai-cli', 'wrappers');
const PROFILE_FILE = path.join(__dirname, 'provider_profiles.json');

export function parseArgs(argv) {
  const result = { account: 'default', action: 'capabilities', headed: false, networkMetadata: false };
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === '--headed') result.headed = true;
    else if (item === '--network-metadata') result.networkMetadata = true;
    else if (item.startsWith('--')) {
      const key = item.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      result[key] = argv[index + 1];
      index += 1;
    }
  }
  return result;
}

export function loadCatalog(profileFile = PROFILE_FILE) {
  const catalog = JSON.parse(fs.readFileSync(profileFile, 'utf8'));
  if (catalog.schema_version !== 1 || !Array.isArray(catalog.providers)) {
    throw new Error('Unsupported wrapper profile catalog.');
  }
  return catalog;
}

export function getProfile(catalog, providerId) {
  const profile = catalog.providers.find((entry) => entry.id === providerId);
  if (!profile) throw new Error(`Unknown wrapper provider: ${providerId}`);
  return profile;
}

export function profileMetadata(profile) {
  return {
    id: profile.id,
    kind: profile.kind,
    state: profile.state,
    source_examples: profile.source_examples,
    allow_send_after_probe: Boolean(profile.allow_send_after_probe),
  };
}

function directoryMode(directory, mode = 0o700) {
  fs.mkdirSync(directory, { recursive: true, mode });
  try { fs.chmodSync(directory, mode); } catch { /* platform may not support chmod */ }
}

export function pathsFor(profileRoot, provider, account) {
  const root = path.resolve(profileRoot || DEFAULT_ROOT);
  const safeProvider = provider.replace(/[^a-z0-9_-]/gi, '_');
  const safeAccount = account.replace(/[^a-z0-9_-]/gi, '_');
  const profileDir = path.join(root, 'profiles', safeProvider, safeAccount);
  const metadataDir = path.join(root, 'status', safeProvider, safeAccount);
  directoryMode(profileDir);
  directoryMode(metadataDir);
  return {
    profileDir,
    metadataDir,
    statusPath: path.join(metadataDir, 'status.json'),
    configPath: path.join(metadataDir, 'profile.json'),
  };
}

export function hashObject(value) {
  return crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex').slice(0, 16);
}

function redactedError(error) {
  const raw = String(error?.message || error || 'runner error');
  return raw
    .replace(/Bearer\s+[^\s]+/gi, 'Bearer [redacted]')
    .replace(/(token|cookie|authorization)=[^\s,]+/gi, '$1=[redacted]')
    .slice(0, 240);
}

function emit(payload, exitCode = null) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  if (exitCode !== null) process.exitCode = exitCode;
}

export function loadStatus(statusPath) {
  if (!fs.existsSync(statusPath)) return null;
  try {
    const parsed = JSON.parse(fs.readFileSync(statusPath, 'utf8'));
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch {
    return null;
  }
}

export function saveStatus(statusPath, payload) {
  const tempPath = `${statusPath}.${process.pid}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(payload, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(tempPath, statusPath);
  try { fs.chmodSync(statusPath, 0o600); } catch { /* platform may not support chmod */ }
}

const LOCAL_PROFILE_FIELDS = new Set(['url', 'state', 'allow_send_after_probe', 'input', 'submit', 'response', 'ready', 'login', 'wait']);

function validateStringArray(value, name) {
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string' || item.length > 512)) {
    throw new Error(`Invalid local profile field '${name}'.`);
  }
  return value;
}

function validateSection(value, name, includeMode = false) {
  if (!value || typeof value !== 'object') throw new Error(`Invalid local profile section '${name}'.`);
  const section = { candidates: validateStringArray(value.candidates, `${name}.candidates`) };
  if (includeMode) {
    if (!['textarea', 'react-textarea', 'contenteditable'].includes(value.mode)) {
      throw new Error('Invalid local profile input mode.');
    }
    section.mode = value.mode;
  }
  return section;
}

export function loadLocalProfile(baseProfile, profilePaths) {
  if (!fs.existsSync(profilePaths.configPath)) return { profile: baseProfile, overridden: false };
  let override;
  try {
    override = JSON.parse(fs.readFileSync(profilePaths.configPath, 'utf8'));
  } catch {
    throw new Error('Local selector profile is not valid JSON.');
  }
  if (!override || typeof override !== 'object') throw new Error('Local selector profile must be an object.');
  for (const key of Object.keys(override)) {
    if (!LOCAL_PROFILE_FIELDS.has(key)) throw new Error(`Local selector profile field '${key}' is not allowed.`);
  }
  const profile = structuredClone(baseProfile);
  if (override.url !== undefined) {
    if (typeof override.url !== 'string' || override.url.length > 2048 || !/^https?:\/\//.test(override.url)) {
      throw new Error('Local selector profile URL must be an http(s) browser URL.');
    }
    profile.url = override.url;
  }
  if (override.state !== undefined) {
    if (override.state !== 'probe-required') throw new Error('Local selector profile may only set state to probe-required.');
    profile.state = override.state;
  }
  if (override.allow_send_after_probe !== undefined) {
    if (override.allow_send_after_probe !== true) throw new Error('Local selector profile may only enable send after a probe.');
    profile.allow_send_after_probe = true;
  }
  if (override.input !== undefined) profile.input = validateSection(override.input, 'input', true);
  for (const section of ['submit', 'response', 'ready', 'login']) {
    if (override[section] !== undefined) profile[section] = validateSection(override[section], section);
  }
  if (override.wait !== undefined) {
    const stable = Number(override.wait.stable_ms);
    const timeout = Number(override.wait.timeout_ms);
    if (!Number.isFinite(stable) || !Number.isFinite(timeout) || stable < 500 || timeout < stable || timeout > 300000) {
      throw new Error('Invalid local selector profile wait values.');
    }
    profile.wait = { stable_ms: stable, timeout_ms: timeout };
  }
  profile.source_examples = [...(baseProfile.source_examples || []), 'local validated selector profile'];
  return { profile, overridden: true };
}

export function readyToSend(profile, status) {
  return Boolean(
    profile.kind === 'browser-wrapper'
      && profile.allow_send_after_probe
      && status
      && status.observed_state === 'send-ready'
      && status.profile_fingerprint === hashObject(profile)
  );
}

function resolveChromium(args) {
  const selected = args.chromium || process.env.MULTI_AI_CHROMIUM_PATH || DEFAULT_CHROMIUM;
  if (!fs.existsSync(selected)) {
    throw new Error('Chromium not found. Set MULTI_AI_CHROMIUM_PATH or pass --chromium <path>.');
  }
  return selected;
}

function loadPuppeteer() {
  const packagePath = process.env.MULTI_AI_PUPPETEER_PACKAGE
    || path.join(REPOSITORY_ROOT, 'deepseek-cli', 'package.json');
  try {
    const require = createRequire(pathToFileURL(packagePath));
    return require('puppeteer');
  } catch {
    throw new Error('Puppeteer is unavailable from the repository lightweight runtime. Install the existing deepseek-cli dependency first.');
  }
}

async function launch(args, profileDir) {
  const puppeteer = loadPuppeteer();
  return puppeteer.launch({
    headless: args.headed ? false : 'new',
    executablePath: resolveChromium(args),
    userDataDir: profileDir,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
}

async function inspectSelector(page, selector, requireActionable = false) {
  try {
    return await page.$eval(selector, (element, actionableRequired) => {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const visible = style.display !== 'none'
        && style.visibility !== 'hidden'
        && Number(style.opacity || 1) > 0
        && rect.width > 0
        && rect.height > 0;
      const disabled = Boolean(element.disabled)
        || element.getAttribute('aria-disabled') === 'true'
        || element.hasAttribute('hidden');
      return { present: true, visible, actionable: visible && (!actionableRequired || !disabled) };
    }, requireActionable);
  } catch {
    return { present: false, visible: false, actionable: false };
  }
}

async function firstFound(page, candidates, requireActionable = false) {
  for (const selector of candidates || []) {
    const inspection = await inspectSelector(page, selector, requireActionable);
    if (inspection.present && inspection.visible && (!requireActionable || inspection.actionable)) {
      return { selector, inspection };
    }
  }
  return { selector: null, inspection: null };
}

async function selectorPresence(page, candidates, requireActionable = false) {
  const result = [];
  for (const selector of candidates || []) {
    result.push({ selector, ...(await inspectSelector(page, selector, requireActionable)) });
  }
  return result;
}

async function openProviderPage(browser, profile) {
  if (!profile.url) throw new Error(`Provider '${profile.id}' has no verified browser URL/profile fixture.`);
  const pages = await browser.pages();
  const page = pages[0] || await browser.newPage();
  await page.goto(profile.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  return page;
}

async function probe(profile, args, profilePaths) {
  if (profile.kind === 'delegated') {
    return { action: 'probe', provider: profile.id, observed_state: 'delegated', profile_fingerprint: hashObject(profile) };
  }
  if (!profile.url) {
    return { action: 'probe', provider: profile.id, observed_state: 'discovery-required', profile_fingerprint: hashObject(profile) };
  }

  const browser = await launch(args, profilePaths.profileDir);
  try {
    const page = await openProviderPage(browser, profile);
    const [input, submit, response, ready, login] = await Promise.all([
      selectorPresence(page, profile.input?.candidates, true),
      selectorPresence(page, profile.submit?.candidates, true),
      selectorPresence(page, profile.response?.candidates, false),
      selectorPresence(page, profile.ready?.candidates, true),
      selectorPresence(page, profile.login?.candidates, false),
    ]);
    const hasInput = input.some((entry) => entry.actionable);
    const hasSubmit = submit.some((entry) => entry.actionable);
    const hasResponse = response.some((entry) => entry.visible);
    const hasReady = ready.some((entry) => entry.actionable);
    const loginNeeded = login.some((entry) => entry.visible) || /sign[_/-]?in|login/i.test(page.url());
    let observedState = profile.state;
    if (loginNeeded) observedState = 'login-needed';
    else if (profile.state === 'probe-required' && hasInput && hasSubmit && hasReady && (profile.response?.candidates || []).length > 0) observedState = 'send-ready';
    else if (profile.state === 'probe-required') observedState = 'selector-drift';

    const metadata = {
      action: 'probe',
      provider: profile.id,
      account: args.account,
      observed_state: observedState,
      profile_fingerprint: hashObject(profile),
      selector_summary: {
        input: hasInput,
        submit: hasSubmit,
        response_observed: hasResponse,
        response_declared: (profile.response?.candidates || []).length > 0,
        ready: hasReady,
        login: loginNeeded,
        selected: {
          input: input.find((entry) => entry.actionable)?.selector || null,
          submit: submit.find((entry) => entry.actionable)?.selector || null,
          response: response.find((entry) => entry.visible)?.selector || null,
          ready: ready.find((entry) => entry.actionable)?.selector || null,
        },
      },
      selector_fingerprint: hashObject({ input, submit, response, ready, login }),
      updated_at: new Date().toISOString(),
    };
    saveStatus(profilePaths.statusPath, metadata);
    return metadata;
  } finally {
    await browser.close();
  }
}

async function connect(profile, args, profilePaths) {
  if (profile.kind === 'delegated') {
    return { action: 'connect', provider: profile.id, observed_state: 'delegated' };
  }
  if (!profile.url) {
    return { action: 'connect', provider: profile.id, observed_state: 'discovery-required' };
  }
  const browser = await launch({ ...args, headed: true }, profilePaths.profileDir);
  const page = await openProviderPage(browser, profile);
  saveStatus(profilePaths.statusPath, {
    action: 'connect', provider: profile.id, account: args.account,
    observed_state: 'connect-requested', profile_fingerprint: hashObject(profile),
    updated_at: new Date().toISOString(),
  });
  emit({ action: 'connect', provider: profile.id, account: args.account, observed_state: 'manual-login', instruction: 'Complete provider-owned sign-in in the visible browser, then stop this command and run probe.' });
  await new Promise((resolve) => {
    const shutdown = async () => { try { await browser.close(); } finally { resolve(); } };
    process.once('SIGINT', shutdown);
    process.once('SIGTERM', shutdown);
    page.once('close', shutdown);
  });
  return null;
}

async function writePrompt(page, selector, mode, prompt) {
  if (mode === 'contenteditable') {
    await page.$eval(selector, (element, text) => {
      element.focus();
      element.textContent = text;
      element.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
    }, prompt);
    return;
  }
  await page.$eval(selector, (element, text) => {
    const prototype = Object.getPrototypeOf(element);
    const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value')
      || Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
    descriptor?.set?.call(element, text);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }, prompt);
}

async function stableText(page, selector, waitConfig) {
  const timeout = Number(waitConfig?.timeout_ms || 120000);
  const stableMs = Number(waitConfig?.stable_ms || 3000);
  const started = Date.now();
  let last = '';
  let stableSince = 0;
  while (Date.now() - started < timeout) {
    let current = '';
    try {
      current = await page.$eval(selector, (element) => (element.innerText || element.textContent || '').trim());
    } catch { current = ''; }
    if (current && current === last) {
      if (!stableSince) stableSince = Date.now();
      if (Date.now() - stableSince >= stableMs) return current;
    } else {
      last = current;
      stableSince = 0;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error('Timed out waiting for a stable browser response.');
}

async function send(profile, args, profilePaths) {
  const status = loadStatus(profilePaths.statusPath);
  if (!readyToSend(profile, status)) {
    throw new Error(`Provider '${profile.id}' is not send-ready. Run connect and then probe for this account first.`);
  }
  if (!args.prompt) throw new Error('Send requires --prompt.');
  const browser = await launch(args, profilePaths.profileDir);
  try {
    const page = await openProviderPage(browser, profile);
    const input = await firstFound(page, profile.input?.candidates, true);
    const submit = await firstFound(page, profile.submit?.candidates, true);
    const response = await firstFound(page, profile.response?.candidates, false);
    if (!input.selector || !submit.selector || !response.selector) throw new Error('Required profile selectors are missing; run probe and update the fixture/profile.');
    await writePrompt(page, input.selector, profile.input.mode, args.prompt);
    await page.click(submit.selector);
    const text = await stableText(page, response.selector, profile.wait);
    return {
      action: 'send', provider: profile.id, account: args.account,
      observed_state: 'completed', response_selector: response.selector,
      elapsed_ms: 0, text,
    };
  } finally {
    await browser.close();
  }
}

export async function run(args, catalog = loadCatalog()) {
  const baseProfile = getProfile(catalog, args.provider);
  const profilePaths = pathsFor(args.profileRoot, baseProfile.id, args.account || 'default');
  const { profile, overridden } = loadLocalProfile(baseProfile, profilePaths);
  if (args.action === 'capabilities') return {
    action: 'capabilities', provider: profile.id, ...profileMetadata(profile),
    local_selector_profile: overridden, status: loadStatus(profilePaths.statusPath),
  };
  if (args.action === 'connect') return connect(profile, args, profilePaths);
  if (args.action === 'probe') return probe(profile, args, profilePaths);
  if (args.action === 'send') return send(profile, args, profilePaths);
  throw new Error(`Unsupported action '${args.action}'.`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.provider) throw new Error('--provider is required.');
  const started = Date.now();
  try {
    const result = await run(args);
    if (result) emit({ ...result, elapsed_ms: result.elapsed_ms || Date.now() - started });
  } catch (error) {
    emit({ action: args.action, provider: args.provider, observed_state: 'error', error: redactedError(error) }, 2);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main();
}
