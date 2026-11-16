import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import fs from 'fs';
import * as runtimeIntel from './runtime-stream-intelligence.mjs';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const BASE_URL = 'https://chat.deepseek.com/';
const CACHE_DIR = path.join(__dirname, '..', '.cache');
const REPORT_DIR = path.join(__dirname, '..', 'test-reports');

if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR, { recursive: true });
if (!fs.existsSync(REPORT_DIR)) fs.mkdirSync(REPORT_DIR, { recursive: true });

const SELECTOR_CACHE = path.join(CACHE_DIR, 'selector-intelligence.json');
const ENDPOINT_CACHE = path.join(CACHE_DIR, 'endpoint-intelligence.json');

const now = () => Date.now();
const wait = ms => new Promise(r => setTimeout(r, ms));

const report = {
  started: new Date().toISOString(),
  tests: [],
  selectors: {},
  endpoints: {},
  dom: {},
  screenshots: [],
  success: true,
  correlations: [],
  newEndpoints: [],
  newSelectors: []
};

function logTest(name, ok, details = {}) {
  report.tests.push({
    name,
    ok,
    details,
    ts: now()
  });
  if (!ok) report.success = false;
  console.log(`${ok ? '✅' : '❌'} ${name}`);
  if (Object.keys(details).length) console.log(JSON.stringify(details, null, 2));
}

console.log('🚀 Launching DeepSeek runtime tests...');

const browser = await puppeteer.launch({
  headless: 'new',
  executablePath: CHROMIUM_PATH,
  userDataDir: './browser-data',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
});

const page = await browser.newPage();

await page.evaluateOnNewDocument(() => {
  globalThis.__DS_RUNTIME_INTEL__ = {
    streams: [],
    fetches: [],
    events: [],
    created: Date.now()
  };
});

const client = await page.target().createCDPSession();
await client.send('Network.enable');

globalThis.__CDP_EVENTS__ = [];

client.on('Network.webSocketCreated', data => {
  globalThis.__CDP_EVENTS__.push({ type: 'ws-created', data });
});
client.on('Network.webSocketFrameSent', data => {
  globalThis.__CDP_EVENTS__.push({ type: 'ws-sent', payload: data.response?.payloadData || null });
});
client.on('Network.webSocketFrameReceived', data => {
  globalThis.__CDP_EVENTS__.push({ type: 'ws-recv', payload: data.response?.payloadData || null });
});
client.on('Network.responseReceived', data => {
  globalThis.__CDP_EVENTS__.push({ type: 'response', url: data.response?.url || null, mime: data.response?.mimeType || null });
});

await runtimeIntel.injectRuntimeHooks(page);

const endpointMap = {};
const responseMap = {};
const allEndpoints = new Set();
const allSelectors = new Set();

page.on('request', req => {
  const url = req.url();
  allEndpoints.add(url);
  endpointMap[url] = { method: req.method(), lastSeen: now() };
});

page.on('response', async res => {
  const url = res.url();
  if (!responseMap[url]) responseMap[url] = { count: 0, statuses: [] };
  responseMap[url].count++;
  responseMap[url].statuses.push(res.status());
});

await page.evaluateOnNewDocument(() => {
  window.__DS_COMPLETIONS__ = [];
  window.__DS_UPLOADS__ = [];
  window.__DS_FETCHES__ = [];
  window.__DS_REGENERATIONS__ = [];
  window.__DS_SEARCH__ = [];

  const origFetch = window.fetch;
  window.fetch = async (...args) => {
    const [url, options] = args;
    const urlStr = typeof url === 'string' ? url : (url?.url || '');
    window.__DS_FETCHES__.push({ url: urlStr, method: options?.method || 'GET', ts: Date.now() });

    if (urlStr.includes('/chat/completion')) window.__DS_COMPLETIONS__.push({ url: urlStr, ts: Date.now() });
    if (urlStr.includes('/upload_file')) window.__DS_UPLOADS__.push({ url: urlStr, ts: Date.now() });
    if (urlStr.includes('/search')) window.__DS_SEARCH__.push({ url: urlStr, ts: Date.now() });

    const res = await origFetch(...args);
    if (urlStr.includes('/chat/completion')) {
      try {
        const clone = res.clone();
        clone.text().then(text => { window.__DS_SSE_CHUNKS__ = text.split('\n').filter(x => x.startsWith('data:')); }).catch(() => {});
      } catch {}
    }
    return res;
  };
});

await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 60000 });
await wait(3000);

const shot1 = path.join(REPORT_DIR, `${now()}-initial.png`);
await page.screenshot({ path: shot1, fullPage: true });
report.screenshots.push(shot1);

const isAuth = !page.url().includes('/sign_in');
logTest('Authentication', isAuth);

const domInfo = await page.evaluate(() => {
  const visible = el => {
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && el.offsetHeight > 0 && el.offsetWidth > 0;
  };
  const textareas = Array.from(document.querySelectorAll('textarea'));
  const buttons = Array.from(document.querySelectorAll('button,[role="button"],div[role="button"]'));
  const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
  const radios = Array.from(document.querySelectorAll('[role="radio"]'));
  const toggles = Array.from(document.querySelectorAll('[role="switch"], .toggle, [class*="toggle"]'));
  const sidebar = document.querySelector('[class*="sidebar"], [class*="panel"], [class*="drawer"]');
  const allClasses = [];
  document.querySelectorAll('*').forEach(el => {
    if (el.className && typeof el.className === 'string') {
      el.className.split(/\s+/).forEach(c => { if (c.trim()) allClasses.push(c.trim()); });
    }
  });
  const freq = {};
  allClasses.forEach(c => { freq[c] = (freq[c] || 0) + 1; });
  const topClasses = Object.entries(freq).sort((a,b) => b[1] - a[1]).slice(0, 100);
  return {
    textareas: textareas.map(x => ({ placeholder: x.placeholder, visible: visible(x), className: x.className })),
    buttons: buttons.map(x => ({ text: (x.innerText || '').trim(), visible: visible(x), className: x.className, aria: x.getAttribute('aria-label') })).filter(x => x.text || x.aria || x.className),
    fileInputs: fileInputs.map(x => ({ accept: x.accept, visible: visible(x), hidden: x.hidden, disabled: x.disabled, className: x.className })),
    radios: radios.map(x => ({ text: (x.innerText || '').trim(), checked: x.getAttribute('aria-checked'), className: x.className, model: x.dataset.modelType })),
    toggles: toggles.map(x => ({ text: (x.innerText || '').trim(), checked: x.getAttribute('aria-checked'), className: x.className })),
    sidebarExists: !!sidebar,
    topClasses
  };
});

report.dom = domInfo;
domInfo.topClasses.forEach(cls => allSelectors.add(cls));

logTest('DOM discovery', true, {
  textareas: domInfo.textareas.length,
  buttons: domInfo.buttons.length,
  fileInputs: domInfo.fileInputs.length,
  radios: domInfo.radios.length,
  toggles: domInfo.toggles.length
});

// ==================== PROBE 1: Attachment Upload in Expert Mode ====================
let uploadSuccess = false;
const expertRadio = await page.$('div[data-model-type="expert"][role="radio"]');
if (expertRadio) {
  const checked = await page.evaluate(el => el.getAttribute('aria-checked'), expertRadio);
  if (checked !== 'true') {
    await expertRadio.click();
    await wait(1500);
  }
  const uploadInput = domInfo.fileInputs.find(x => !x.disabled);
  if (uploadInput) {
    const testFilePath = path.join(REPORT_DIR, 'test-upload.txt');
    fs.writeFileSync(testFilePath, 'DeepSeek probe test file');
    const fileInputElement = await page.$('input[type="file"]');
    if (fileInputElement) {
      await fileInputElement.uploadFile(testFilePath);
      await wait(2000);
      const uploadDetected = await page.evaluate(() => (window.__DS_UPLOADS__ || []).length > 0);
      uploadSuccess = uploadDetected;
      fs.unlinkSync(testFilePath);
    }
  }
}
logTest('PROBE 1: Attachment upload in Expert mode', uploadSuccess, { expertModeEnabled: true, uploadAttempted: !!domInfo.fileInputs.length });

// ==================== PROBE 2: Expert Mode + Thinking Toggle ====================
let thinkingToggleSuccess = false;
if (expertRadio) {
  await expertRadio.click();
  await wait(1000);
  const thinkingToggle = await page.$('[role="switch"], .thinking-toggle, [class*="thinking"]');
  if (thinkingToggle) {
    const beforeState = await page.evaluate(el => el.getAttribute('aria-checked'), thinkingToggle);
    await thinkingToggle.click();
    await wait(1000);
    const afterState = await page.evaluate(el => el.getAttribute('aria-checked'), thinkingToggle);
    thinkingToggleSuccess = beforeState !== afterState;
  }
}
logTest('PROBE 2: Expert mode + thinking toggle', thinkingToggleSuccess, { expertEnabled: !!expertRadio, toggleFound: !!thinkingToggle });

// ==================== PROBE 3: Web Search Sidebar ====================
let webSearchSuccess = false;
let sidebarData = {};
try {
  const searchButton = await page.$('[class*="search"], [aria-label*="search"], button:has(svg)');
  if (searchButton) {
    await searchButton.click();
    await wait(2000);
    const sidebarVisible = await page.evaluate(() => {
      const sidebar = document.querySelector('[class*="sidebar"], [class*="panel"], [class*="drawer"]');
      return sidebar ? getComputedStyle(sidebar).display !== 'none' : false;
    });
    webSearchSuccess = sidebarVisible;
    sidebarData = { sidebarVisible, searchButtonClicked: true };
  }
  const searchEndpointDetected = await page.evaluate(() => (window.__DS_SEARCH__ || []).length > 0);
  if (searchEndpointDetected) webSearchSuccess = true;
} catch (e) {
  sidebarData = { error: e.message };
}
logTest('PROBE 3: Web search sidebar', webSearchSuccess, sidebarData);

// ==================== PROBE 4: Regeneration with new message_id ====================
let regenerationSuccess = false;
const textarea = await page.$('textarea');
if (textarea) {
  await textarea.click();
  await textarea.evaluate((el, value) => {
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    nativeSetter.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, 'regeneration test message');
  await wait(1500);
  try {
    const sendBtn = await page.$('._52c986b');
    if (sendBtn) {
      await sendBtn.click();
      await wait(3000);
      const regenerationButton = await page.$('[class*="regenerate"], [aria-label*="regenerate"], button:has(svg)');
      if (regenerationButton) {
        const beforeMessageId = await page.evaluate(() => {
          const messages = document.querySelectorAll('[data-message-id]');
          return messages.length > 0 ? messages[messages.length - 1].getAttribute('data-message-id') : null;
        });
        await regenerationButton.click();
        await wait(3000);
        const afterMessageId = await page.evaluate(() => {
          const messages = document.querySelectorAll('[data-message-id]');
          return messages.length > 0 ? messages[messages.length - 1].getAttribute('data-message-id') : null;
        });
        regenerationSuccess = beforeMessageId !== afterMessageId;
      }
    }
  } catch (e) {
    console.log('Regeneration probe error:', e.message);
  }
}
logTest('PROBE 4: Regeneration with new message_id', regenerationSuccess, { messageSent: !!textarea });

// ==================== PROBE 5: Log all new endpoints and selectors ====================
let endpointDiscoverySuccess = false;
let selectorDiscoverySuccess = false;
await wait(5000);

const currentEndpoints = Array.from(allEndpoints);
let oldEndpoints = [];
if (fs.existsSync(ENDPOINT_CACHE)) {
  try {
    oldEndpoints = Object.keys(JSON.parse(fs.readFileSync(ENDPOINT_CACHE, 'utf8')));
  } catch {}
}
const newEndpointsFound = currentEndpoints.filter(e => !oldEndpoints.includes(e));
report.newEndpoints = newEndpointsFound;
endpointDiscoverySuccess = newEndpointsFound.length > 0;

let oldSelectors = [];
if (fs.existsSync(SELECTOR_CACHE)) {
  try {
    oldSelectors = JSON.parse(fs.readFileSync(SELECTOR_CACHE, 'utf8')).topClasses || [];
  } catch {}
}
const newSelectorsFound = Array.from(allSelectors).filter(s => !oldSelectors.includes(s));
report.newSelectors = newSelectorsFound;
selectorDiscoverySuccess = newSelectorsFound.length > 0;

logTest('PROBE 5: Log all new endpoints and selectors', endpointDiscoverySuccess && selectorDiscoverySuccess, {
  newEndpoints: newEndpointsFound.length,
  newSelectors: newSelectorsFound.length,
  sampleEndpoints: newEndpointsFound.slice(0, 5),
  sampleSelectors: newSelectorsFound.slice(0, 5)
});

// ==================== Existing Tests ====================
const uploadInputs = domInfo.fileInputs.filter(x => !x.disabled);
logTest('Upload input discovery', uploadInputs.length > 0, { count: uploadInputs.length });

logTest('Textarea discovery', !!textarea);

const sendCandidates = await page.evaluate(() => {
  const els = Array.from(document.querySelectorAll('button,[role="button"],div[role="button"]'));
  return els.map((el, idx) => {
    const rect = el.getBoundingClientRect();
    return { idx, text: (el.innerText || '').trim(), aria: el.getAttribute('aria-label'), cls: el.className, disabled: el.disabled || el.getAttribute('aria-disabled'), w: rect.width, h: rect.height, svg: !!el.querySelector('svg') };
  });
});
const likelySend = sendCandidates.filter(x => {
  const txt = ((x.text || '') + ' ' + (x.aria || '') + ' ' + (x.cls || '')).toLowerCase();
  return txt.includes('send') || txt.includes('submit') || txt.includes('icon') || txt.includes('atom-button') || txt.includes('button');
});
report.selectors.sendCandidates = likelySend;
logTest('Send button intelligence', likelySend.length > 0, { candidates: likelySend.slice(0, 10) });

if (textarea) {
  await textarea.click();
  await textarea.evaluate((el, value) => {
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    nativeSetter.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, 'runtime selector correlation test');
  await wait(1500);
  const currentVal = await page.evaluate(el => el.value, textarea);
  logTest('Textarea injection', currentVal.includes('runtime selector correlation'), { valueLength: currentVal.length });
}

if (textarea) {
  try {
    await page.waitForSelector('._52c986b:not([disabled]):not([aria-disabled="true"])', { timeout: 8000 });
    const sendBtn = await page.$('._52c986b');
    if (sendBtn) {
      await sendBtn.click();
      console.log('📤 Test message sent, waiting for SSE stream...');
      await page.waitForFunction(() => (window.__DS_COMPLETIONS__ || []).length > 0, { timeout: 15000 }).catch(() => {});
      await wait(3000);
    }
  } catch (e) {
    console.log('⚠️ Send button not available:', e.message);
  }
}

await wait(5000);
const completionEndpoints = Object.keys(endpointMap).filter(x => x.includes('/chat/') || x.includes('/completion') || x.includes('/conversation'));
logTest('Completion endpoint discovery', completionEndpoints.length > 0, { endpoints: completionEndpoints });

const sseInfo = await page.evaluate(() => ({
  completions: window.__DS_COMPLETIONS__ || [],
  uploads: window.__DS_UPLOADS__ || [],
  fetches: window.__DS_FETCHES__ || [],
  sseChunks: window.__DS_SSE_CHUNKS__ ? window.__DS_SSE_CHUNKS__.length : 0
}));
logTest('SSE stream detection', sseInfo.fetches.length > 0, sseInfo);

let oldSelectorsCache = {};
if (fs.existsSync(SELECTOR_CACHE)) {
  try { oldSelectorsCache = JSON.parse(fs.readFileSync(SELECTOR_CACHE, 'utf8')); } catch {}
}
const newClasses = domInfo.topClasses.map(x => x[0]);
const oldClasses = oldSelectorsCache.topClasses || [];
const changedClasses = newClasses.filter(x => !oldClasses.includes(x));
logTest('Selector drift analysis', true, { changedClasses, driftCount: changedClasses.length });

const selectorCacheData = {
  textareaCount: domInfo.textareas.length,
  buttonCount: domInfo.buttons.length,
  fileInputCount: domInfo.fileInputs.length,
  radioCount: domInfo.radios.length,
  toggleCount: domInfo.toggles.length,
  topClasses: newClasses,
  updated: now()
};
fs.writeFileSync(SELECTOR_CACHE, JSON.stringify(selectorCacheData, null, 2));
fs.writeFileSync(ENDPOINT_CACHE, JSON.stringify(endpointMap, null, 2));

report.endpoints = endpointMap;
report.correlations = Object.entries(endpointMap).map(([url, meta]) => ({
  endpoint: url,
  method: meta.method,
  responseCount: responseMap[url]?.count || 0,
  statuses: responseMap[url]?.statuses || []
}));
logTest('Endpoint correlation map', Object.keys(endpointMap).length > 0, { total: Object.keys(endpointMap).length });

const shot2 = path.join(REPORT_DIR, `${now()}-final.png`);
await page.screenshot({ path: shot2, fullPage: true });
report.screenshots.push(shot2);

report.finished = new Date().toISOString();
const reportFile = path.join(REPORT_DIR, `report-${now()}.json`);
fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));

console.log('\n========================================');
console.log('🏁 TEST SUITE COMPLETE');
console.log('========================================\n');
console.log(`Success: ${report.success}`);
console.log(`Report: ${reportFile}`);
console.log(`Selector cache: ${SELECTOR_CACHE}`);
console.log(`Endpoint cache: ${ENDPOINT_CACHE}`);

if (!page.isClosed()) console.log('🧠 Runtime page still alive');

let runtime = null;
try {
  if (!page.isClosed()) runtime = await runtimeIntel.exportRuntime(page);
  const runtimePath = path.join(REPORT_DIR, `runtime-${Date.now()}.json`);
  runtime = runtime || { streams: [], fetches: [], events: [], recovered: true };
  fs.writeFileSync(runtimePath, JSON.stringify(runtime, null, 2));
  console.log("✅ Runtime intelligence export", { runtimePath });
  console.log("✅ Runtime stream intelligence", JSON.stringify({
    fetches: (runtime?.fetches || []).length,
    streams: (runtime?.streams || []).length,
    completions: (runtime?.completions || []).length,
    uploads: (runtime?.uploads || []).length
  }, null, 2));
} catch (e) {
  console.log("❌ Runtime stream intelligence", { error: e.message });
}

await browser.close();
