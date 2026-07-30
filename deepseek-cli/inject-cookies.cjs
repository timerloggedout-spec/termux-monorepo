const puppeteer = require('puppeteer');
const fs = require('fs');

const COOKIES_FILE = process.argv[2] || './cookies_2.json';
const USER_DATA_DIR = process.argv[3] || './browser-data-account2-v2';
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

  const browser = await puppeteer.launch({
    headless: 'new', executablePath: CHROMIUM_PATH,
    userDataDir: USER_DATA_DIR,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  
  // Set cookies on blank page
  await page.goto('about:blank');
  await page.setCookie(...cookieParams);
  console.log(`🍪 ${cookieParams.length} cookies injected into ${USER_DATA_DIR}`);
  
  // Verify by navigating
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  const url = page.url();
  console.log('📍 Page URL:', url);
  
  if (url.includes('/sign_in')) {
    console.log('❌ Still sign-in. Cookies may be stale.');
  } else {
    console.log('✅ Authenticated! Profile saved with Account 2 cookies.');
  }
  await browser.close();
})();
