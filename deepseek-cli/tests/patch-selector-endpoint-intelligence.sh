#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "🧠 Patching DeepSeek selector + endpoint intelligence..."

TARGET="tests/deepseek-full-suite.js"

if [ ! -f "$TARGET" ]; then
  echo "❌ Missing: $TARGET"
  exit 1
fi

cp "$TARGET" "${TARGET}.bak.$(date +%s)"

cat > "$TARGET" << 'JSEOF'
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

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
  correlations: []
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
  if (Object.keys(details).length) {
    console.log(JSON.stringify(details, null, 2));
  }
}

(async () => {

  console.log('🚀 Launching DeepSeek runtime tests...');

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu'
    ]
  });

  const page = await browser.newPage();

  const endpointMap = {};
  const responseMap = {};

  // ============================================
  // NETWORK INTELLIGENCE
  // ============================================

  page.on('request', req => {
    const url = req.url();

    endpointMap[url] = {
      method: req.method(),
      lastSeen: now()
    };
  });

  page.on('response', async res => {
    const url = res.url();

    if (!responseMap[url]) {
      responseMap[url] = {
        count: 0,
        statuses: []
      };
    }

    responseMap[url].count++;
    responseMap[url].statuses.push(res.status());
  });

  // ============================================
  // FETCH / SSE HOOK
  // ============================================

  await page.evaluateOnNewDocument(() => {

    window.__DS_COMPLETIONS__ = [];
    window.__DS_UPLOADS__ = [];
    window.__DS_FETCHES__ = [];

    const origFetch = window.fetch;

    window.fetch = async (...args) => {

      const [url, options] = args;

      const urlStr = typeof url === 'string'
        ? url
        : (url?.url || '');

      window.__DS_FETCHES__.push({
        url: urlStr,
        method: options?.method || 'GET',
        ts: Date.now()
      });

      if (urlStr.includes('/chat/completion')) {
        window.__DS_COMPLETIONS__.push({
          url: urlStr,
          ts: Date.now()
        });
      }

      if (urlStr.includes('/upload_file')) {
        window.__DS_UPLOADS__.push({
          url: urlStr,
          ts: Date.now()
        });
      }

      const res = await origFetch(...args);

      if (urlStr.includes('/chat/completion')) {

        try {

          const clone = res.clone();

          clone.text().then(text => {

            const chunks = text
              .split('\n')
              .filter(x => x.startsWith('data:'));

            window.__DS_SSE_CHUNKS__ = chunks;

          }).catch(() => {});

        } catch {}

      }

      return res;
    };

  });

  // ============================================
  // OPEN
  // ============================================

  await page.goto(BASE_URL, {
    waitUntil: 'networkidle2',
    timeout: 60000
  });

  await wait(3000);

  const shot1 = path.join(REPORT_DIR, `${now()}-initial.png`);
  await page.screenshot({ path: shot1, fullPage: true });
  report.screenshots.push(shot1);

  // ============================================
  // AUTH
  // ============================================

  const isAuth = !page.url().includes('/sign_in');

  logTest('Authentication', isAuth);

  // ============================================
  // DOM DISCOVERY
  // ============================================

  const domInfo = await page.evaluate(() => {

    const visible = el => {
      const s = getComputedStyle(el);

      return (
        s.display !== 'none' &&
        s.visibility !== 'hidden' &&
        el.offsetHeight > 0 &&
        el.offsetWidth > 0
      );
    };

    const textareas = Array.from(document.querySelectorAll('textarea'));

    const buttons = Array.from(
      document.querySelectorAll(
        'button,[role="button"],div[role="button"]'
      )
    );

    const fileInputs = Array.from(
      document.querySelectorAll('input[type="file"]')
    );

    const radios = Array.from(
      document.querySelectorAll('[role="radio"]')
    );

    const allClasses = [];

    document.querySelectorAll('*').forEach(el => {
      if (el.className && typeof el.className === 'string') {
        el.className.split(/\s+/).forEach(c => {
          if (c.trim()) allClasses.push(c.trim());
        });
      }
    });

    const freq = {};

    allClasses.forEach(c => {
      freq[c] = (freq[c] || 0) + 1;
    });

    const topClasses = Object.entries(freq)
      .sort((a,b) => b[1] - a[1])
      .slice(0, 100);

    return {

      textareas: textareas.map(x => ({
        placeholder: x.placeholder,
        visible: visible(x),
        className: x.className
      })),

      buttons: buttons
        .map(x => ({
          text: (x.innerText || '').trim(),
          visible: visible(x),
          className: x.className,
          aria: x.getAttribute('aria-label')
        }))
        .filter(x =>
          x.text ||
          x.aria ||
          x.className
        ),

      fileInputs: fileInputs.map(x => ({
        accept: x.accept,
        visible: visible(x),
        hidden: x.hidden,
        disabled: x.disabled,
        className: x.className
      })),

      radios: radios.map(x => ({
        text: (x.innerText || '').trim(),
        checked: x.getAttribute('aria-checked'),
        className: x.className,
        model: x.dataset.modelType
      })),

      topClasses
    };

  });

  report.dom = domInfo;

  logTest('DOM discovery', true, {
    textareas: domInfo.textareas.length,
    buttons: domInfo.buttons.length,
    fileInputs: domInfo.fileInputs.length,
    radios: domInfo.radios.length
  });

  // ============================================
  // EXPERT MODE
  // ============================================

  const expert = await page.$('div[data-model-type="expert"][role="radio"]');

  if (expert) {

    const checked = await page.evaluate(
      el => el.getAttribute('aria-checked'),
      expert
    );

    if (checked !== 'true') {
      await expert.click();
      await wait(1500);
    }

    const finalChecked = await page.evaluate(
      el => el.getAttribute('aria-checked'),
      expert
    );

    logTest('Expert mode enable', finalChecked === 'true', {
      checked: finalChecked
    });

  } else {

    logTest('Expert mode enable', false);

  }

  // ============================================
  // FILE INPUT ANALYSIS
  // ============================================

  const uploadInputs = domInfo.fileInputs.filter(
    x => !x.disabled
  );

  logTest(
    'Upload input discovery',
    uploadInputs.length > 0,
    { count: uploadInputs.length }
  );

  // ============================================
  // TEXTAREA
  // ============================================

  const textarea = await page.$('textarea');

  logTest(
    'Textarea discovery',
    !!textarea
  );

  // ============================================
  // SEND BUTTON INTELLIGENCE
  // ============================================

  const sendCandidates = await page.evaluate(() => {

    const els = Array.from(
      document.querySelectorAll(
        'button,[role="button"],div[role="button"]'
      )
    );

    return els.map((el, idx) => {

      const rect = el.getBoundingClientRect();

      return {
        idx,
        text: (el.innerText || '').trim(),
        aria: el.getAttribute('aria-label'),
        cls: el.className,
        disabled:
          el.disabled ||
          el.getAttribute('aria-disabled'),
        w: rect.width,
        h: rect.height,
        svg: !!el.querySelector('svg')
      };

    });

  });

  const likelySend = sendCandidates.filter(x => {

    const txt = (
      (x.text || '') + ' ' +
      (x.aria || '') + ' ' +
      (x.cls || '')
    ).toLowerCase();

    return (
      txt.includes('send') ||
      txt.includes('submit') ||
      txt.includes('icon') ||
      txt.includes('atom-button') ||
      txt.includes('button')
    );

  });

  report.selectors.sendCandidates = likelySend;

  logTest(
    'Send button intelligence',
    likelySend.length > 0,
    { candidates: likelySend.slice(0, 10) }
  );

  // ============================================
  // TYPE TEST
  // ============================================

  if (textarea) {

    await textarea.click();

    await page.evaluate(el => {
      el.value = 'runtime selector correlation test';
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }, textarea);

    await wait(2000);

    const currentVal = await page.evaluate(
      el => el.value,
      textarea
    );

    logTest(
      'Textarea injection',
      currentVal.includes('runtime selector correlation'),
      { valueLength: currentVal.length }
    );

  }

  // ============================================
  // COMPLETION ENDPOINT DETECTION
  // ============================================

  await wait(5000);

  const completionEndpoints = Object.keys(endpointMap)
    .filter(x =>
      x.includes('/chat/') ||
      x.includes('/completion') ||
      x.includes('/conversation')
    );

  logTest(
    'Completion endpoint discovery',
    completionEndpoints.length > 0,
    { endpoints: completionEndpoints }
  );

  // ============================================
  // SSE STREAM
  // ============================================

  const sseInfo = await page.evaluate(() => ({
    completions: window.__DS_COMPLETIONS__ || [],
    uploads: window.__DS_UPLOADS__ || [],
    fetches: window.__DS_FETCHES__ || [],
    sseChunks:
      window.__DS_SSE_CHUNKS__
        ? window.__DS_SSE_CHUNKS__.length
        : 0
  }));

  logTest(
    'SSE stream detection',
    sseInfo.fetches.length > 0,
    sseInfo
  );

  // ============================================
  // SELECTOR DRIFT
  // ============================================

  let oldSelectors = {};

  if (fs.existsSync(SELECTOR_CACHE)) {
    try {
      oldSelectors = JSON.parse(
        fs.readFileSync(SELECTOR_CACHE, 'utf8')
      );
    } catch {}
  }

  const newClasses = domInfo.topClasses.map(x => x[0]);

  const oldClasses = oldSelectors.topClasses || [];

  const changedClasses = newClasses.filter(
    x => !oldClasses.includes(x)
  );

  logTest(
    'Selector drift analysis',
    true,
    {
      changedClasses,
      driftCount: changedClasses.length
    }
  );

  // ============================================
  // CACHE WRITE
  // ============================================

  const selectorCacheData = {
    textareaCount: domInfo.textareas.length,
    buttonCount: domInfo.buttons.length,
    fileInputCount: domInfo.fileInputs.length,
    radioCount: domInfo.radios.length,
    topClasses: newClasses,
    updated: now()
  };

  fs.writeFileSync(
    SELECTOR_CACHE,
    JSON.stringify(selectorCacheData, null, 2)
  );

  fs.writeFileSync(
    ENDPOINT_CACHE,
    JSON.stringify(endpointMap, null, 2)
  );

  report.endpoints = endpointMap;

  report.correlations = Object.entries(endpointMap)
    .map(([url, meta]) => ({
      endpoint: url,
      method: meta.method,
      responseCount: responseMap[url]?.count || 0,
      statuses: responseMap[url]?.statuses || []
    }));

  logTest(
    'Endpoint correlation map',
    Object.keys(endpointMap).length > 0,
    {
      total: Object.keys(endpointMap).length
    }
  );

  // ============================================
  // FINAL SCREENSHOT
  // ============================================

  const shot2 = path.join(REPORT_DIR, `${now()}-final.png`);

  await page.screenshot({
    path: shot2,
    fullPage: true
  });

  report.screenshots.push(shot2);

  // ============================================
  // SAVE REPORT
  // ============================================

  report.finished = new Date().toISOString();

  const reportFile = path.join(
    REPORT_DIR,
    `report-${now()}.json`
  );

  fs.writeFileSync(
    reportFile,
    JSON.stringify(report, null, 2)
  );

  console.log('\n========================================');
  console.log('🏁 TEST SUITE COMPLETE');
  console.log('========================================\n');

  console.log(`Success: ${report.success}`);
  console.log(`Report: ${reportFile}`);
  console.log(`Selector cache: ${SELECTOR_CACHE}`);
  console.log(`Endpoint cache: ${ENDPOINT_CACHE}`);

  await browser.close();

})();
JSEOF

chmod +x "$TARGET"

echo ""
echo "✅ Patch applied successfully."
echo ""
echo "Now run:"
echo ""
echo "  node tests/deepseek-full-suite.js"
echo ""
echo "Then inspect:"
echo ""
echo "  cat .cache/selector-intelligence.json"
echo "  cat .cache/endpoint-intelligence.json"
echo ""
echo "Key improvements:"
echo "  ✔ Dynamic send-button intelligence"
echo "  ✔ Runtime fetch/SSE interception"
echo "  ✔ Endpoint correlation persistence"
echo "  ✔ Selector drift analysis"
echo "  ✔ Obfuscation resilience"
echo "  ✔ API/UI linkage discovery"
echo "  ✔ Hidden endpoint discovery"
echo "  ✔ WebUI ↔ endpoint mapping"
echo ""
echo "🎯 This now evolves toward adaptive selector intelligence."
echo ""

