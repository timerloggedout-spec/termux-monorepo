const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });
  const page = await browser.newPage();
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2' });
  // Wait until the app is fully hydrated
  await page.waitForSelector('textarea[placeholder="Message DeepSeek"]', { timeout: 30000 });

  // Dump any global objects that look like a POW solver
  const solverInfo = await page.evaluate(() => {
    const results = [];
    // Check common global variable names
    const candidates = ['__pow', 'pow', 'solvePow', 'solveChallenge', 'deepseekPow', 'computeAnswer'];
    for (const key of candidates) {
      if (window[key] && typeof window[key] === 'function') {
        results.push({ key, source: window[key].toString().substring(0, 200) });
      }
    }
    // Also look for any object with 'DeepSeekHashV1' string
    const allKeys = Object.keys(window);
    for (const key of allKeys) {
      try {
        const val = window[key];
        if (typeof val === 'function' && val.toString().includes('DeepSeekHashV1')) {
          results.push({ key, source: val.toString().substring(0, 200) });
        }
      } catch {}
    }
    return results;
  });
  console.log('🔍 POW solver candidates:', JSON.stringify(solverInfo, null, 2));
  await browser.close();
})();
