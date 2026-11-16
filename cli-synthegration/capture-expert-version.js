const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: '/data/data/com.termux/files/home/deepseek-cli/browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  let versionHeaders = {};
  page.on('request', req => {
    const h = req.headers();
    if (req.url().includes('/api/v0/chat/completion')) {
      versionHeaders = {
        'x-client-version': h['x-client-version'],
        'x-app-version': h['x-app-version'],
        'x-client-locale': h['x-client-locale'],
        'x-client-platform': h['x-client-platform'],
        'authorization': h['authorization']?.slice(0,20) + '...'
      };
    }
  });
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  // click Expert radio
  const expert = await page.$('div[data-model-type="expert"][role="radio"]');
  if (expert) { await expert.click(); await new Promise(r=>setTimeout(r,1000)); }
  // type and send
  const input = await page.$('textarea');
  if (input) {
    await input.type('hi');
    await new Promise(r=>setTimeout(r,500));
    const send = await page.$('div[role="button"]');
    if (send) await send.click();
    await new Promise(r=>setTimeout(r,5000));
  }
  console.log(JSON.stringify(versionHeaders, null, 2));
  await browser.close();
})();
