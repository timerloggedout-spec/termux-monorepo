const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const COOKIES_FILE = process.argv[2] || './cookies_2.json';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

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

  // Intercept API requests for Bearer token
  page.on('request', req => {
    const auth = req.headers()['authorization'];
    if (auth && auth.startsWith('Bearer ') && !capturedToken) {
      capturedToken = auth.replace('Bearer ', '');
      console.log('🔑 Token captured from:', req.url().substring(0, 60));
    }
  });

  // SET COOKIES ON BLANK PAGE FIRST
  await page.goto('about:blank');
  await page.setCookie(...cookieParams);
  console.log('🍪 ' + cookieParams.length + ' cookies set on blank page.');

  // Navigate to DeepSeek
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('📍 Page URL:', page.url().substring(0, 50));
  await new Promise(r => setTimeout(r, 3000));

  // Force API call if needed
  if (!capturedToken) {
    console.log('⏳ Triggering API call...');
    try {
      await page.evaluate(async () => { await fetch('/api/v0/chat_session/fetch_page'); });
      await new Promise(r => setTimeout(r, 2000));
    } catch (e) {}
  }

  if (capturedToken) {
    console.log('TOKEN:' + capturedToken);
    fs.writeFileSync(path.join(__dirname, 'token_account2.txt'), capturedToken);
    console.log('✅ Token saved to token_account2.txt');
  } else {
    console.log('❌ No token captured. Page URL:', page.url());
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('Page snippet:', bodyText.substring(0, 200));
  }
  await browser.close();
})();
