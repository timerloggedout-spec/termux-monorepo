const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    headless: false,  // need visible for Expert click to register
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  
  const page = await browser.newPage();
  let capturedHeaders = {};
  let captureDone = false;
  
  // Intercept ALL requests to find the one with Expert headers
  await page.setRequestInterception(true);
  page.on('request', req => {
    const url = req.url();
    const headers = req.headers();
    if (url.includes('/api/v0/chat/completion') && !captureDone) {
      capturedHeaders = {
        url: url,
        'x-client-version': headers['x-client-version'],
        'x-app-version': headers['x-app-version'],
        'x-client-platform': headers['x-client-platform'],
        'x-client-locale': headers['x-client-locale'],
        'authorization': headers['authorization'] ? headers['authorization'].substring(0,30) + '...' : 'none',
        'content-type': headers['content-type'],
        'origin': headers['origin'],
        'referer': headers['referer'],
      };
      captureDone = true;
      fs.writeFileSync('./expert-headers.json', JSON.stringify(capturedHeaders, null, 2));
      console.log('CAPTURED EXPERT HEADERS:', JSON.stringify(capturedHeaders, null, 2));
    }
    req.continue();
  });
  
  console.log('Navigating to DeepSeek...');
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  
  // Click Expert radio
  try {
    await page.waitForSelector('div[data-model-type="expert"]', { timeout: 5000 });
    await page.click('div[data-model-type="expert"]');
    console.log('Expert selected');
    await new Promise(r => setTimeout(r, 1000));
  } catch(e) {
    console.log('Could not click Expert:', e.message);
  }
  
  // Type and send
  try {
    await page.waitForSelector('textarea', { timeout: 5000 });
    await page.type('textarea', 'hi');
    await new Promise(r => setTimeout(r, 500));
    // Find the send button
    const sendBtn = await page.$('div[role="button"]');
    if (sendBtn) {
      await sendBtn.click();
      console.log('Message sent, waiting for response...');
      await new Promise(r => setTimeout(r, 8000));
    }
  } catch(e) {
    console.log('Send error:', e.message);
  }
  
  console.log('\n=== FINAL CAPTURED HEADERS ===');
  console.log(JSON.stringify(capturedHeaders, null, 2));
  fs.writeFileSync('./expert-headers.json', JSON.stringify(capturedHeaders, null, 2));
  
  await browser.close();
})();
