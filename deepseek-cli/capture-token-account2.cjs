const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const COOKIES_FILE = path.resolve(process.argv[2] || './cookies_2.json');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

(async () => {
  const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const cookies = Array.isArray(cookiesRaw) ? cookiesRaw : (cookiesRaw.cookies || []);
  
  const cookieParams = cookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: c.path || '/',
    expires: c.expirationDate || -1,
    httpOnly: c.httpOnly || false,
    secure: c.secure || false,
    sameSite: c.sameSite || 'Lax',
  }));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });

  const page = await browser.newPage();
  
  // Intercept API requests to grab the Bearer token
  let capturedToken = null;
  page.on('request', req => {
    const authHeader = req.headers()['authorization'];
    if (authHeader && authHeader.startsWith('Bearer ') && !capturedToken) {
      capturedToken = authHeader.replace('Bearer ', '');
      console.log('🔑 Token captured from API request to:', req.url());
    }
  });

  try {
    // Visit base domain and set cookies
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.setCookie(...cookieParams);
    console.log('🍪 Cookies loaded from:', COOKIES_FILE);
    
    // Navigate to chat – this triggers API calls
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Wait for network activity
    await new Promise(r => setTimeout(r, 3000));
    
    // If still no token, force an API call
    if (!capturedToken) {
      console.log('⏳ No token intercepted yet. Triggering API call...');
      await page.evaluate(async () => {
        await fetch('/api/v0/chat_session/fetch_page');
      });
      await new Promise(r => setTimeout(r, 2000));
    }
    
    if (capturedToken) {
      console.log('TOKEN:' + capturedToken);
      // Save to file
      const outFile = path.join(__dirname, 'token_account2.txt');
      fs.writeFileSync(outFile, capturedToken);
      console.log('✅ Token saved to:', outFile);
    } else {
      console.log('❌ No token captured. Page URL:', page.url());
      console.log('Page title:', await page.title());
      process.exit(1);
    }
  } finally {
    await browser.close();
  }
})();
