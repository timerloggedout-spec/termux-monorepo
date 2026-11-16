const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  let captured = {};
  page.on('request', req => {
    if (req.url().includes('/api/v0/chat/completion')) {
      captured['x-client-version'] = req.headers()['x-client-version'];
      captured['x-app-version'] = req.headers()['x-app-version'];
      captured['x-client-platform'] = req.headers()['x-client-platform'];
      captured['x-client-locale'] = req.headers()['x-client-locale'];
    }
  });
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  try {
    await page.waitForSelector('div[data-model-type="expert"][role="radio"]', { timeout: 5000 });
    await page.click('div[data-model-type="expert"][role="radio"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.type('textarea', 'hi');
    await new Promise(r => setTimeout(r, 500));
    await page.click('div[role="button"]');
    await new Promise(r => setTimeout(r, 6000));
  } catch(e) { console.log('Interaction failed:', e.message); }
  console.log(JSON.stringify(captured, null, 2));
  await browser.close();
})();
