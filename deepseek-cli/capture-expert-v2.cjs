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
      const h = req.headers();
      captured = {
        'x-client-version': h['x-client-version'] || h['X-Client-Version'],
        'x-app-version': h['x-app-version'] || h['X-App-Version'],
        'x-client-platform': h['x-client-platform'] || h['X-Client-Platform'],
        'x-client-locale': h['x-client-locale'] || h['X-Client-Locale'],
      };
      console.log('Captured headers:', JSON.stringify(captured));
    }
  });
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('Page loaded, selecting Expert...');
  try {
    await page.waitForSelector('div[data-model-type="expert"]', { timeout: 5000 });
    await page.click('div[data-model-type="expert"]');
    console.log('Expert clicked');
    await new Promise(r => setTimeout(r, 1000));
    await page.waitForSelector('textarea', { timeout: 5000 });
    await page.type('textarea', 'hi');
    await new Promise(r => setTimeout(r, 500));
    await page.click('div[role="button"]');
    console.log('Sent, waiting for completion...');
    await new Promise(r => setTimeout(r, 8000));
  } catch(e) { console.log('Interaction error:', e.message); }
  console.log('Final captured:', JSON.stringify(captured));
  await browser.close();
})();
