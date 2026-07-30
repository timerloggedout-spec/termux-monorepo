const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setRequestInterception(true);
  let expertHeaders = null;
  
  page.on('request', req => {
    const h = req.headers();
    if (req.url().includes('/api/v0/chat/completion') && !expertHeaders) {
      expertHeaders = {
        'x-client-version': h['x-client-version'] || '',
        'x-app-version': h['x-app-version'] || '',
        'x-client-platform': h['x-client-platform'] || '',
        'x-client-locale': h['x-client-locale'] || '',
      };
      require('fs').writeFileSync('./expert-headers.json', JSON.stringify(expertHeaders, null, 2));
      console.log('CAPTURED:', JSON.stringify(expertHeaders));
    }
    req.continue();
  });

  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('Page loaded. Clicking Expert...');
  await page.waitForSelector('div[data-model-type="expert"]', { timeout: 5000 });
  await page.click('div[data-model-type="expert"]');
  console.log('Expert clicked. Typing and sending...');
  await new Promise(r => setTimeout(r, 800));
  await page.type('textarea', 'test');
  await new Promise(r => setTimeout(r, 500));
  await page.click('div[role="button"]');
  console.log('Sent. Waiting for response...');
  await new Promise(r => setTimeout(r, 6000));
  
  if (expertHeaders) {
    console.log('\n=== EXPERT HEADERS ===');
    console.log(JSON.stringify(expertHeaders, null, 2));
  } else {
    console.log('\nNo completion request captured. Dumping all API requests seen:');
    // Re-check by monitoring all requests
  }
  await browser.close();
})();
