const puppeteer = require('puppeteer');
const fs = require('fs');

const COOKIES_FILE = process.argv[2] || './cookies_fresh_account2.json';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const FIREFOX_UA = 'Mozilla/5.0 (Android 15; Mobile; rv:140.0) Gecko/140.0 Firefox/140.0';

(async () => {
  const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const cookies = Array.isArray(cookiesRaw) ? cookiesRaw : (cookiesRaw.cookies || []);
  const cookieParams = cookies.map(c => ({
    name: c.name, value: c.value, domain: c.domain,
    path: c.path || '/', expires: c.expirationDate || -1,
    httpOnly: c.httpOnly || false, secure: c.secure || false,
    sameSite: c.sameSite || 'Lax',
  }));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });

  const page = await browser.newPage();

  // EXACT replication of the working deepseek-debug3.js: set Firefox UA BEFORE anything
  await page.setUserAgent(FIREFOX_UA);
  console.log('🦊 Firefox User-Agent set.');

  // Set cookies on blank page
  await page.goto('about:blank');
  await page.setCookie(...cookieParams);
  console.log('🍪 ' + cookieParams.length + ' cookies set on blank page.');

  // Navigate to DeepSeek
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  const url = page.url();
  console.log('📍 Page URL:', url);

  if (url.includes('/sign_in')) {
    console.log('❌ Still sign-in — cookies may be stale.');
    process.exit(1);
  }

  console.log('✅ Authenticated! Extracting token from localStorage...');

  // Read the Bearer token from localStorage (same as deepterm does)
  const token = await page.evaluate(() => {
    return localStorage.getItem('userToken');
  });

  if (token) {
    console.log('TOKEN:' + token);
    fs.writeFileSync('token_account2.txt', token);
    console.log('✅ Account 2 Bearer token saved to token_account2.txt');
  } else {
    console.log('❌ No token found in localStorage.');
    process.exit(1);
  }

  await browser.close();
})();
