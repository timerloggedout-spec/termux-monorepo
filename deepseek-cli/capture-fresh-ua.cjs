const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const COOKIES_FILE = process.argv[2] || './cookies_2.json';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

const FIREFOX_UA = 'Mozilla/5.0 (Android 15; Mobile; rv:140.0) Gecko/140.0 Firefox/140.0';

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const cookies = Array.isArray(cookiesRaw) ? cookiesRaw : (cookiesRaw.cookies || []);
  const cookieParams = cookies.map(c => ({
    name: c.name, value: c.value, domain: c.domain,
    path: c.path || '/', expires: c.expirationDate || -1,
    httpOnly: c.httpOnly || false, secure: c.secure || false,
    sameSite: c.sameSite || 'Lax',
  }));

  let capturedToken = null;
  const browser = await puppeteer.launch({
    headless: 'new', executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });

  const page = await browser.newPage();

  // SET USER AGENT TO MATCH FIREFOX
  await page.setUserAgent(FIREFOX_UA);
  console.log('🦊 User-Agent set to Firefox.');

  // Intercept
  page.on('request', req => {
    const auth = req.headers()['authorization'];
    if (auth && auth.startsWith('Bearer ') && !capturedToken) {
      capturedToken = auth.replace('Bearer ', '');
      console.log('🔑 Token captured from:', req.url().substring(0, 60));
    }
  });

  // Set cookies on blank page
  await page.goto('about:blank');
  await page.setCookie(...cookieParams);
  console.log('🍪 ' + cookieParams.length + ' cookies set.');

  // Navigate
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('📍 Page URL:', page.url());

  if (page.url().includes('/sign_in')) {
    console.log('❌ Still sign-in with Firefox UA.');
    process.exit(1);
  }

  console.log('✅ Authenticated! Waiting for API calls...');
  await wait(4000);

  // Trigger an API call to force token capture
  if (!capturedToken) {
    console.log('⏳ Triggering API call...');
    try {
      await page.evaluate(async () => {
        await fetch('/api/v0/chat_session/fetch_page');
      });
      await wait(3000);
    } catch (e) {}
  }

  if (capturedToken) {
    console.log('TOKEN:' + capturedToken);
    fs.writeFileSync(path.join(__dirname, 'token_account2.txt'), capturedToken);
    console.log('✅ Account 2 token saved.');
  } else {
    console.log('❌ No token captured');
    process.exit(1);
  }

  await browser.close();
})();
