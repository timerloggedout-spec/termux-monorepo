const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  
  // Capture from browser context directly
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('Page loaded. Clicking Expert...');
  await page.waitForSelector('div[data-model-type="expert"]', { timeout: 5000 });
  await page.click('div[data-model-type="expert"]');
  console.log('Expert clicked. Typing and sending...');
  await new Promise(r => setTimeout(r, 800));
  await page.type('textarea', 'test');
  await new Promise(r => setTimeout(r, 500));
  await page.click('div[role="button"]');
  console.log('Sent. Extracting headers from browser...');
  await new Promise(r => setTimeout(r, 3000));
  
  // Read headers from the browser's own fetch calls
  const headers = await page.evaluate(() => {
    // Intercept next fetch to capture headers
    return new Promise((resolve) => {
      const origFetch = window.fetch;
      window.fetch = function(url, options = {}) {
        window.fetch = origFetch;
        const h = {};
        if (options.headers) {
          if (options.headers instanceof Headers) {
            for (const [k,v] of options.headers.entries()) h[k] = v;
          } else if (typeof options.headers === 'object') {
            Object.assign(h, options.headers);
          }
        }
        // Only capture completion requests
        if (url.includes && url.includes('completion')) {
          resolve(h);
        } else {
          resolve(h); // capture any API call
        }
        return origFetch.apply(this, arguments);
      };
      // Trigger a new request by sending another message
      setTimeout(() => resolve({timeout: true}), 5000);
    });
  });
  
  console.log('Captured headers:', JSON.stringify(headers, null, 2));
  require('fs').writeFileSync('./expert-headers.json', JSON.stringify(headers, null, 2));
  await browser.close();
})();
